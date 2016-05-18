import React, { Component } from 'react'
import {connect} from 'react-redux'
import isEmpty from 'lodash/isEmpty'
import {loadStatsFromDVID, fetchStatsIfNeeded} from './actions'
import {OverallSection, DailySection, UserSection} from './components'
import 'whatwg-fetch'



class App extends Component {
	componentDidMount() {
		const dvid_api_url = `${this.props.dvid_url}/api/node/${this.props.uuid}/external_dashboard/key/dashboard`
		this.props.getStats(dvid_api_url)
		// fetch(dvid_api_url).then( (response) => {
		// 	return  response.json()
		// }).then( (r) => {
		// 	this.props.fetchFromDVID(dvid_api_url, r)
		// 	this.render()
		// })
	}

	render() {
		let overall, timeseries, user
		let overallSection, dailySection, userSection
		if (!isEmpty(this.props.stats)) {
			overall = this.props.stats.overall
			timeseries = this.props.stats.timeseries
			user = this.props.stats.user
			overallSection = <OverallSection title='Totals' overall={overall} />
			dailySection = <DailySection title='Daily Statistics' timeseries={timeseries} />
			userSection = <UserSection title='User Statistics' user={user} />
		}
		return (
			<div>
				{overallSection}
				{dailySection}
				{userSection}
			</div>
		)
	}
}



const mapStateToProps = function(state){
	//const {url, payload} = state.dvidData 
	const {selectedDVID, newdvidData} = state
	const {isFetching,  didInvalidate, lastUpdated, stats} = newdvidData || {
			isFetching: false,
			didInvalidate: false,
			lastUpdated: 0,
			stats: {},
		} 
	return {
		url: selectedDVID,
		stats: stats
	}
};
const mapDispatchToProps = function(dispatch){
	return {
		getStats: function(url) {
			dispatch(fetchStatsIfNeeded(url))
		}
	}
}

// const mapDispatchToProps = function(dispatch){
// 	return {
// 		fetchFromDVID: function(url, data){ 
// 			dispatch(loadStatsFromDVID(url, data)) 
// 		},
// 		fetchStats,
// 	}
// };

export default connect(mapStateToProps, mapDispatchToProps)(App)
