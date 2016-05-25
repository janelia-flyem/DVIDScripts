import React, { Component } from 'react'
import {connect} from 'react-redux'
import isEmpty from 'lodash/isEmpty'
import {fetchStatsIfNeeded, selectProofreader} from './actions'
import {OverallSection, DailySection, UserSection} from './components'
import 'whatwg-fetch'



class App extends Component {
	componentDidMount() {
		const dvid_api_url = `${this.props.dvid_url}/api/node/${this.props.uuid}/external_dashboard/key/dashboard`
		this.props.getStats(dvid_api_url)
	}

	render() {
		let overall, timeseries, user
		let overallSection, dailySection, userSection, loadingSection
		if (!isEmpty(this.props.stats)) {
			overall = this.props.stats.overall
			timeseries = this.props.stats.timeseries
			user = this.props.stats.user
			const selectedProofreader = this.props.proofreader
			const proofreaders = Object.keys(user)
			overallSection = <OverallSection title='Totals' overall={overall} />
			dailySection = <DailySection title='Daily Statistics' timeseries={timeseries} />
			userSection = <UserSection title='User Statistics' user={user} allProofreaders={proofreaders} proofreader={selectedProofreader} onSelectProofreader={this.props.changeProofreader} />
		}
		else {
			loadingSection = <div><h1>Fetching Data from DVID</h1></div>
		}
		return (
			<div>
				{loadingSection}
				{overallSection}
				{dailySection}
				{userSection}
			</div>
		)
	}
}

const mapStateToProps = function(state){
	//const {url, payload} = state.dvidData 
	const {selectedDVID, dvidData, proofreader} = state
	const {isFetching, didInvalidate, lastUpdated, stats} = (!isEmpty(dvidData))? dvidData: {
			isFetching: false,
			didInvalidate: false,
			lastUpdated: 0,
			stats: {}
		}
	return {
		url: selectedDVID,
		stats,
		proofreader
	}
}

const mapDispatchToProps = function(dispatch){
	return {
		getStats: function(url) {
			dispatch(fetchStatsIfNeeded(url))
		},
		changeProofreader: function(proofreader) {
			dispatch(selectProofreader(proofreader))
		}
	}
}



export default connect(mapStateToProps, mapDispatchToProps)(App)
