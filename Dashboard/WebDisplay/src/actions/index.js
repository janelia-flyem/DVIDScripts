import isEmpty from 'lodash/isEmpty'

export const LOAD_FROM_DVID = 'LOAD_FROM_DVID'
export const SELECT_DVID = 'SELECT_DVID'
export const INVALIDATE_DVID_DATA = 'INVALIDATE_DVID_DATA'
export const REQUEST_STATS_FROM_DVID = 'REQUEST_STATS_FROM_DVID'
export const RECEIVE_STATS_FROM_DVID = 'RECEIVE_STATS_FROM_DVID'
export const SELECT_PROOFREADER = 'SELECT_PROOFREADER'


export const requestStatsFromDVID = (url) => {
	return {
		type: REQUEST_STATS_FROM_DVID,
		url
	}
}

export function receiveStatsFromDVID(url, payload) {
  return {
    type: RECEIVE_STATS_FROM_DVID,
    url,
    payload,
    receivedAt: Date.now()
  }
}

export function selectDVID(dvid) {
  return {
    type: SELECT_DVID,
    dvid
  }
}

export function invalidateDVIDData(dvid) {
  return {
    type: INVALIDATE_DVID_DATA,
    dvid
  }
}

export function selectProofreader(proofreader) {
	return {
		type: SELECT_PROOFREADER,
		proofreader
	}
}

function fetchStats(url) {
  return dispatch => {
    dispatch(requestStatsFromDVID(url))
    return fetch(url)
      .then(response => {
      	return response.json()
      })
      .then(data => {
      	return dispatch(receiveStatsFromDVID(url, data))
      })
  }
}

function shouldFetchStats(state, url) {
  const stats = state.dvidData
  if (isEmpty(stats.stats)) {
    return true
  }
  if (stats.isFetching) {
    return false
  }
  return state.didInvalidate
}

export function fetchStatsIfNeeded(url) {
  return (dispatch, getState) => {
    if (shouldFetchStats(getState(), url)) {
      return dispatch(fetchStats(url))
    }
  }
}
