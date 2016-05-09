import React, { Component } from 'react'
import {connect} from 'react-redux'
import {loadStatsFromDVID} from './actions'
import {OverallSection, DailySection, UserSection} from './components'
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
		let overall, timeseries, user
		let overallSection, dailySection, userSection
		if (this.props.stats) {
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
	const {url, payload} = state.dvidData 
	return {
		url,
		stats: payload
	}
};

const mapDispatchToProps = function(dispatch){
	return {
		fetchFromDVID: function(url, data){ 
			dispatch(loadStatsFromDVID(url, data)) 
		},
	}
};

export default connect(mapStateToProps, mapDispatchToProps)(App)