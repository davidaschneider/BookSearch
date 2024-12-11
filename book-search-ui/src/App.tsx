
import React from 'react';
import ReactDOM from 'react-dom';
import './App.css'
import 'bootstrap/dist/css/bootstrap.min.css'


import BookSearch from './BookSearch';

// Use ReactDOM to bootstrap the application inside the HTML element #root
let root = document.getElementById('root');
if (root) {
  ReactDOM.render(<>
    <BookSearch/>
  </>, root);
}

export default BookSearch
