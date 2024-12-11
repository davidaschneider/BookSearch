//external
import React, { ChangeEvent } from 'react';
import { action, makeObservable, observable } from 'mobx';
import { observer } from 'mobx-react';

import Button from 'react-bootstrap/Button';
import { Form, InputGroup } from 'react-bootstrap';

//internal
import Book from 'Book';
import { bookSearch, isbnLookup } from 'api';
import { BookData, LOADING } from 'types';


type BookSearchProps = {
	storeName: string,
	applicationImage: string
}

type status = 'loading' | 'done' | 'fresh'

@observer class BookSearch extends React.Component<BookSearchProps> {
	static defaultProps = {
		storeName: "Book City",
		applicationImage: 'assets/book-city.jpg'
	}

	constructor(props: BookSearchProps) {
		super(props);
		makeObservable(this);
	}

	componentDidMount() {
		// disposeOnUnmount(this, () => {console.log("Unmounting the book search"));
	}

	@observable searchText: string = ""
	@action setSearchText = (e: ChangeEvent<HTMLInputElement>) => { this.searchText = e.target.value }
	@observable books: Array<BookData> = []
	@observable currentStatus: status = 'fresh'
	totalAvailable: number
	page:number = 0
	searchError: string = ''

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
								<Button disabled={this.currentStatus == 'loading' || !this.searchText} onClick={this.performSearch}>Search</Button>
							</InputGroup>
						</div>
					</div>
					<div className='search-results'>
						{this.searchError &&
						<div className='error'>{this.searchError}</div>}
						{this.currentStatus == 'done' && this.totalAvailable &&
						 <div className='count'>Showing {this.books.length} of {this.totalAvailable} total results</div>}

						{this.books.map((b, i) => <Book {...b} key={b.isbn ?? i} />	)}

						{this.currentStatus != 'fresh' && this.totalAvailable > this.books.length &&
						<Button disabled={this.currentStatus == 'loading'} onClick={this.getMore}>
							Get More
						</Button>}
					</div>
					{this.currentStatus == 'done' && this.books.length === 0 ?
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

	@action doSearch = async() => {
		this.currentStatus = 'loading'
		try {
			let {books, total_available} = await bookSearch(this.searchText, this.page)
			this.currentStatus = 'done'
			this.totalAvailable = total_available
			this.books.push(...books.map(b => {
				return {
					...b,
					cover_url: b.cover_url ?? LOADING,
					summary: b.summary ?? LOADING
				}
			}))
			this.books.forEach(async (b, i) => {
				try {
					if (!b.isbn) {
						throw new Error("No ISBN number")
					} else if (this.books[i].isbn == b.isbn && !b.fully_enriched) {
						this.books[i] = await isbnLookup(b.isbn)
					}
				} catch (e) {
					this.books[i].summary = <div className='lighter'>Summary Unavailable</div>
				}
			})
		} catch (e) {
			this.searchError = "An error was encountered during the search."
			console.warn(e)
		} finally {
			this.currentStatus = 'done'
		}	
	}

	@action reset = () => {
		this.books.length = 0
		this.totalAvailable = 0;
		this.page = 1
		this.searchError = ''
	}
}

export default BookSearch;