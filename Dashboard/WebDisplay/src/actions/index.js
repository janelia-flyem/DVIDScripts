export const loadStatsFromDVID = (url, payload) => {
	return {
		type: 'LOAD_FROM_DVID',
		'url': url,
		'payload': payload
	}
}