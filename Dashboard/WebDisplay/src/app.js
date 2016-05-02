import React, { Component } from 'react'
import {connect} from 'react-redux'
import {loadStatsFromDVID} from './actions'
import {SingleStat, Panel} from './components'
import DaySnapshot from './components/day_snapshot'
import {calcDailyMergeSplit, calcDailyMergeSplitChart, calcUserMergeSplitTable, calcDaySnapshotData} from './helpers/utils'
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
		let overall, timeseries, user, merges, splits, dailyTable, dailyChart, userChart, daySnapshot, daySnapshotData, userMergeSplitTableValues, valuesForTable, valuesForChart
		let classMap = {'working': 'DarkTurquoise', 'default': 'white'}
		if (this.props.stats) {
			overall = this.props.stats.overall
			timeseries = this.props.stats.timeseries
			user = this.props.stats.user
			valuesForTable = calcDailyMergeSplit(timeseries.daily)
			valuesForChart = calcDailyMergeSplitChart(timeseries.daily)
			userMergeSplitTableValues = calcUserMergeSplitTable(user)
			daySnapshotData = calcDaySnapshotData(user)
			// TODO check if stats exist
			merges = <SingleStat stat_name='Merges' stat_value={overall.merges} />
			splits = <SingleStat stat_name='Splits' stat_value={overall.splits} />
			dailyTable = <Panel size={6} title='Stats per Day' type='table' value={valuesForTable} />
			dailyChart = <Panel size={6} title='Daily Chart' type='chart' value={valuesForChart} />
			userChart = <Panel size={6} title='Total Merges and Splits by User' type='table' value={userMergeSplitTableValues} />
			daySnapshot = <DaySnapshot barwidth={400}  data={daySnapshotData} height={15} colors={classMap} byweek={false}  />
		}
		return (
			<div>
				<div className='row'>
					<div className='col-lg-12'>
						<div className='panel panel-default'>
							<div className='panel-heading'>
							<h3>Totals</h3> 
							</div>
							<div className='panel-body'>
								{merges}{splits}
							</div>
						</div>
					</div>
				</div>
				<div className='row'>
					<div className='col-lg-12'>
						<div className='panel panel-default'>
							<div className='panel-heading'>
							<h3>Daily Statistics</h3> 
							</div>
							<div className='panel-body'>
								{dailyTable} {dailyChart}
							</div>
						</div>
					</div>
				</div>
				<div className='row'>
					<div className='col-lg-12'>
						<div className='panel panel-default'>
							<div className='panel-heading'>
							<h3>User Statistics</h3> 
							</div>
							<div className='panel-body'>
								{userChart} 
								<div className='col-lg-6'>
									<div className="panel panel-primary">
										<div className="panel-heading">
											Day Snapshot for Proofreaders
										</div>
										<div className="panel-body">{daySnapshot}
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		)
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