import React from 'react'
import { render } from 'react-dom'
import { createStore } from 'redux'
import { Provider } from 'react-redux'
import webDisplayApp from './reducers'
import App from './app'
console.log(webDisplayApp)

let store = createStore(webDisplayApp);

render(
	<Provider store={store}>
		<App />
	</Provider>,
	document.getElementById('content')
);