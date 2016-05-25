import { combineReducers } from 'redux'
//import dvidData from './data'
import {SELECT_DVID, SELECT_PROOFREADER, INVALIDATE_DVID_DATA, REQUEST_STATS_FROM_DVID, RECEIVE_STATS_FROM_DVID} from '../actions'

/*
CORRECT WAY
 */
function selectedDVID(state = 'fakedvid', action){
  switch (action.type) {
    case SELECT_DVID:
    	if (action.dvid) return action.dvid
    	else return state
    default:
      return state
  }
}

const dvidDataInitialState = {
	isFetching: false,
	didInvalidate: false,
	lastUpdated: 0,
	stats: {},
}

function dvidData(state = dvidDataInitialState, action) {
  switch (action.type) {
    case INVALIDATE_DVID_DATA:
	    return Object.assign({}, state, {
	        didInvalidate: true
	      })
    case REQUEST_STATS_FROM_DVID:
       return Object.assign({}, state, {
        isFetching: true,
        didInvalidate: false
      })
    case RECEIVE_STATS_FROM_DVID:
      return Object.assign({}, state, {
        isFetching: false,
        didInvalidate: false,
        stats: action.payload,
        lastUpdated: action.receivedAt
      })
    default:
      return state
  }
}

function proofreader(state=null, action){
	switch (action.type) {
		case SELECT_PROOFREADER:
			console.log("New proofreader")
			if (action.proofreader != ' ') return action.proofreader
			else return state 
		default:
			return state 
	}
}



const webDisplayApp = combineReducers({
 	selectedDVID,
	dvidData,
	proofreader
})

export default webDisplayApp