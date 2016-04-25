import React from 'react'
import { render } from 'react-dom'
import { createStore } from 'redux'
import { Provider } from 'react-redux'
import webDisplayApp from './reducers'
import App from './app'
// console.log(webDisplayApp)

let store = window.my_store = createStore(webDisplayApp);

render(
	<Provider store={store}>
		<App uuid={'edc03'} dvid_url={'http://emdata1.int.janelia.org:8500'} />
	</Provider>,
	document.getElementById('content')
);