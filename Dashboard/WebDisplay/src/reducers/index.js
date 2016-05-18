import { combineReducers } from 'redux'
//import dvidData from './data'
import {SELECT_DVID, INVALIDATE_DVID_DATA, REQUEST_STATS_FROM_DVID, RECEIVE_STATS_FROM_DVID} from '../actions'

/*
OLD WAY
 */
const initialState = {}

const dvidData = (state = initialState, action) => {
  switch (action.type) {
    case 'LOAD_FROM_DVID':
      return Object.assign({}, state, {
        url: action.url,
        payload: action.payload,
      })
    default:
      return state
  }
}

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

function newdvidData(state = dvidDataInitialState, action) {
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



const webDisplayApp = combineReducers({
	dvidData,
	selectedDVID,
	newdvidData
})

export default webDisplayApp