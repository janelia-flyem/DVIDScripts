export const LOAD_FROM_DVID = 'LOAD_FROM_DVID'
export const SELECT_DVID = 'SELECT_DVID'
export const INVALIDATE_DVID_DATA = 'INVALIDATE_DVID_DATA'
export const REQUEST_STATS_FROM_DVID = 'REQUEST_STATS_FROM_DVID'
export const RECEIVE_STATS_FROM_DVID = 'RECEIVE_STATS_FROM_DVID'

export const loadStatsFromDVID = (url, payload) => {
	return {
		type: LOAD_FROM_DVID,
		'url': url,
		'payload': payload
	}
}


