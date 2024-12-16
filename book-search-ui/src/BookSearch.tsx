//external
import React, { ChangeEvent } from 'react';
import { action, makeObservable, observable } from 'mobx';
import { observer } from 'mobx-react';

import Button from 'react-bootstrap/Button';
import { Form, InputGroup } from 'react-bootstrap';

//internal
import Book from 'Book';
import { bookSearch, isbnLookup } from 'api';
import { SummaryStatus, BookData } from 'types';
import pLimit from 'p-limit';


type BookSearchProps = {
	storeName: string,
	applicationImage: string,
	//The default number of simultaneous processs that will run to retrieve summaries.
	summaryPlimit: number,
}

type status = 'loading' | 'done' | 'fresh'

@observer class BookSearch extends React.Component<BookSearchProps> {
	static defaultProps = {
		storeName: "Book City",
		applicationImage: 'assets/book-city.jpg',
		summaryPlimit: 2
	}

	constructor(props: BookSearchProps) {
		super(props);
		makeObservable(this);
		this.summaryLimit = pLimit(props.summaryPlimit)
	}

	componentDidMount() {
		// disposeOnUnmount(this, () => {console.log("Unmounting the book search"));
	}

	@observable searchText: string = ""
	@action setSearchText = (e: ChangeEvent<HTMLInputElement>) => { this.searchText = e.target.value }
	// An array of book IDs (isbn numbers) in the search result order.
	@observable bookIds: Array<string> = []
	@observable booksByISBN: {[key:string]: BookData} = {}
	@observable currentStatus: status = 'fresh'
	totalAvailable: number
	page:number = 0
	@observable searchError: string = ''
	// a p-limit used for throttling the calls to get summaries.
	summaryLimit: pLimit.Limit

	handleKeyDown = (e) => {
		if (e.key == 'Enter') {
			this.performSearch()
		}
	}

	render() {
		return (
			<div className="component-book-search">
				<div className='content'>
					<div className='top-section'>
						<div className='branding'>
							<img src={this.props.applicationImage}/>
							<div className='label'>{this.props.storeName}</div>
						</div>
						<div className='search-bar' onKeyDown={this.handleKeyDown}>
							<InputGroup id='search'>
								<Form.Control placeholder='Enter a book title'
									onChange={this.setSearchText} value={this.searchText}/>
								<LoadingButton  loading={this.currentStatus == 'loading'}   disabled={this.currentStatus == 'loading' || !this.searchText} onClick={this.performSearch}>Search
								</LoadingButton>
							</InputGroup>
						</div>
					</div>
					<div className='search-results'>
						{this.searchError &&
						<div className='error'>{this.searchError}</div>}
						{this.currentStatus == 'done' && this.totalAvailable &&
						 <div className='count'>Showing {this.bookIds.length} of {this.totalAvailable} total results</div>}

						{this.bookIds.map((id, i) => <Book onExtend={() => this.booksByISBN[id].shortened = false} {...this.booksByISBN[id]} key={id} />	)}
						{/* {this.books.map((b, i) => <Book {...this.booksByISBN[String(b)]} key={b ?? i} />	)} */}

						{this.currentStatus != 'fresh' && this.totalAvailable > this.bookIds.length &&
						<LoadingButton loading={this.currentStatus == 'loading'} disabled={this.currentStatus == 'loading'} onClick={this.getMore}>
							Get More
						</LoadingButton>}
					</div>
					{this.currentStatus == 'done' && this.bookIds.length === 0 ?
					<div>No Results Available</div> :
					null}
				</div>
			</div>);
	}

	@action performSearch = async () => {
		this.reset()
		this.doSearch()
	}

	@action getMore = async () => {
		this.page += 1
		this.doSearch()
	}

	@action doSearch = async () => {
		this.currentStatus = 'loading'
		try {
			let { books, total_available } = await bookSearch(this.searchText, this.page)
			this.currentStatus = 'done'
			this.totalAvailable = total_available
			let newBooks = books.filter(b => b.isbn)
								.map(b => {
										return {
											...b,
											cover_url: b.cover_url ?? '',
											summary: b.summary ?? '' as string,
											summaryStatus : !b.summary ? 'loading' as SummaryStatus : null,
											shortened: true,
										}
									})
								
			newBooks.forEach(b => {
						this.bookIds.push(b.isbn as string)
						this.booksByISBN[String(b.isbn)] = b
					})
			this.getSummaries(newBooks)
			this.fetchSummaries(newBooks)
		} catch (e) {
			this.searchError = "An error was encountered during the search."
			console.warn(e)
		} finally {
			this.currentStatus = 'done'
		}
	}


	@action getSummaries = (books: Array<BookData>) => {
		isbnLookup(books.filter(b => !b.cover_url)
						.map((b) => b.isbn as string), ['cover_url']).then(books => {
								books.forEach(b => this.booksByISBN[b.isbn ?? ''].cover_url = b.cover_url ?? '')
							})
	}

	@action fetchSummaries = (books: Array<BookData>) => {
		books.filter(b => !b.summary && (!b.summaryStatus || b.summaryStatus == 'loading'))
			 .forEach((b) => {
				this.summaryLimit(async () => {
					try {
						if (!b.isbn) {
							throw new Error("No ISBN number")
						} else {
							this.booksByISBN[b.isbn].summaryStatus = 'generating'
							let res = await isbnLookup([b.isbn], ['summary'])
							this.booksByISBN[b.isbn].summary = res[0].summary
						}
					} catch (e) {
						if (b.isbn) { this.booksByISBN[b.isbn].summary = 'unavailable' }
					} finally {
						if (b.isbn) { this.booksByISBN[b.isbn].summaryStatus = null }
					}
				})
			})
	}

	@action reset = () => {
		this.bookIds.length = 0
		for (const key in this.booksByISBN) {
			delete this.booksByISBN[key]
		}
		this.totalAvailable = 0;
		this.page = 1
		this.searchError = ''
	}
}

/**
 * A new type of button that adds a 'loading' prop to the standard bootstrap button.  
 * If that prop is truthy, a loading spinner will be shown inside the button
 */
const LoadingButton = props => {
	const {loading, ...attrs} = props
	return (
		<Button {...attrs}>{props.children}
			<span className='loading-container'>
				{props.loading ? <img src={require('assets/spinner.svg').default} alt='Loading'/> : null}
			</span>
		</Button>
	)
}

export default BookSearch;