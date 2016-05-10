import React from 'react'
import { render } from 'react-dom'
import { createStore, applyMiddleware  } from 'redux'
import { Provider } from 'react-redux'
import thunkMiddleware from 'redux-thunk'
import createLogger from 'redux-logger'
import webDisplayApp from './reducers'
import App from './app'

const loggerMiddleware = createLogger()
const store = createStore(webDisplayApp, {}, applyMiddleware(thunkMiddleware))
//let store = window.my_store = createStore(webDisplayApp, {}, window.devToolsExtension ? window.devToolsExtension() : undefined);

render(
	<Provider store={store}>
		<App uuid={'edc03'} dvid_url={'http://emdata1.int.janelia.org:8500'} />
	</Provider>,
	document.getElementById('content')
);