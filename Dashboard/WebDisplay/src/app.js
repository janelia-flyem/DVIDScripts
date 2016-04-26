import React, { Component } from 'react'
import {connect} from 'react-redux'
import {loadStatsFromDVID} from './actions'
import {SingleStat, Panel} from './components'
import {calcDailyMergeSplit} from './helpers/utils'
import 'whatwg-fetch'



class App extends Component {
	componentDidMount() {
		const dvid_api_url = `${this.props.dvid_url}/api/node/${this.props.uuid}/external_dashboard/key/dashboard`
		fetch(dvid_api_url).then( (response) => {
			return  response.json()
		}).then( (r) => {
			this.props.fetchFromDVID(dvid_api_url, r)
			this.render()
		})
	}

	render() {
		let overall, timeseries, user, merges, splits, dailyTable, valuesForTable
		if (this.props.stats) {
			overall = this.props.stats.overall
			timeseries = this.props.stats.timeseries
			user = this.props.stats.user
			valuesForTable = calcDailyMergeSplit(timeseries.daily)
			console.log(valuesForTable)
			// TODO check if stats exist
			merges = <SingleStat stat_name='Merges' stat_value={overall.merges} />
			splits = <SingleStat stat_name='Splits' stat_value={overall.splits} />
			dailyTable = <Panel size={6} title='Stats per Day' type='table' value={valuesForTable} />
		}
		return <div className='row' >{merges}{splits}{dailyTable} </div>
	}
}



var mapStateToProps = function(state){
	const {url, payload} = state.dvidData 
	return {
		url,
		stats: payload
	}
};

var mapDispatchToProps = function(dispatch){
	return {
		fetchFromDVID: function(url, data){ 
			dispatch(loadStatsFromDVID(url, data)) 
		},
	}
};

export default connect(mapStateToProps, mapDispatchToProps)(App)