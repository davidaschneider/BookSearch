//external
import React from 'react';
import { computed, makeObservable } from 'mobx';
import { observer } from 'mobx-react';
import { SummaryStatus } from 'types';

//internal

type BookProps = {
    title: string,
    cover_url: string | null,
    authors: Array<string>,
    summary: string | null ,
    summaryStatus:  SummaryStatus,
    onExtend: () => void,
    shortened?: boolean,
}

@observer class Book extends React.Component<BookProps> {

	constructor(props: BookProps) {
		super (props);
		makeObservable(this);
	}

	componentDidMount() {
		// disposeOnUnmount(this, () => console.log("Unmounting a book"));
	}

    @computed
    get authors () { return this.props.authors?.join(', ')}

    render() {
		return (
			<div className="component-book">
                <div className='cover'>
                    {this.props.cover_url ?
                        <img className='cover-img' src={this.props.cover_url}></img> :
                        null
                    }
                </div>
                <div className='book-data'>
                    <div className='title'>{this.props.title}</div>
                    {this.props.authors?.length > 0 ? 
                        <div className='author'>By&nbsp;
                            {this.authors}
                        </div> : 
                        null}

                    <div className={`summary ${this.props.shortened ? 'shortened block-ellipsis' : ''}`}>
                    {
                     this.props.summary ? 
                     <div onClick={this.props.onExtend}>{this.props.summary}</div> : 
                     (this.props.summaryStatus == 'generating') ?
                     <div className='lighter'>Whipping up a summary...</div> :
                     (this.props.summaryStatus == 'loading') ?
                     <div className='lighter'>Waiting for Summary...</div> : 
                     (this.props.summaryStatus == 'unavailable') ?
                     <div className='lighter'>Summary Unavailable.</div> : null}
                    </div>
                </div>
            </div>
    );
  }

}

export default Book