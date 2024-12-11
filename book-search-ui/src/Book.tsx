//external
import React, { ReactNode } from 'react';
import { computed, makeObservable } from 'mobx';
import { observer } from 'mobx-react';

//internal
import { LOADING } from 'types';


type BookProps = {
    title: string,
    cover_url: string | null,
    authors: Array<string>,
    summary: string | null | ReactNode
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
                    {this.props.cover_url && this.props.cover_url != LOADING ?
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

                    <div className='summary'>

                    {(this.props.summary && this.props.summary != LOADING) ?
                     this.props.summary : 
                     (this.props.summary == LOADING) ?
                     <div className='lighter'>Loading Summary...</div> : null}
                    </div>
                </div>
            </div>
    );
  }

}

export default Book