import React from 'react'
import {calcDailyMergeSplit, calcDailyMergeSplitChart, calcUserMergeSplitTable, calcActivityTraceData, calcUserChartValues, calcUserBodyTimeChart} from '../helpers/utils'
import Griddle from 'griddle-react'
import ReactHighcharts from 'react-highcharts' 
import HighchartsMore from 'highcharts-more'
import ActivityTrace from 'react-activity-trace'
HighchartsMore(ReactHighcharts.Highcharts)

export const SingleStat = (props) => {
	return (
		<div className="col-lg-3">
			<div className="alert alert-info text-center">
				<h4>{props.stat_name}: <b>{props.stat_value} </b></h4>
			</div>
		</div>
	)
}

export const Panel = (props) => {
	let content 
	let colSize = `col-lg-${props.size}`
	if (props.children) {
		content = props.children
	}
	return (
	 	<div className={colSize}>
			<div className="panel panel-primary">
				<div className="panel-heading">
					{props.title}
				</div>
				<div className="panel-body">
					{content}
				</div>
			</div>
		</div>
	)
}


export const Section = (props) => {
	let content
	if (props.children) {
		content = props.children
	}
	return (
		<div className='row'>
			<div className='col-lg-12'>
				<div className='panel panel-default'>
					<div className='panel-heading'>
					<h3>{props.title}</h3> 
					</div>
					<div className='panel-body'>
						{content}
					</div>
				</div>
			</div>
		</div>
	)
}

export const OverallSection = (props) => {
	let merges, splits
	const overall = props.overall
	if (overall.merges) merges = <SingleStat stat_name='Merges' stat_value={overall.merges} />
	if (overall.splits) splits = <SingleStat stat_name='Splits' stat_value={overall.splits} />
	return (
		<Section title={props.title} >
			{merges} {splits}
		</Section>
	)
}

export const DailySection = (props) => {
	let valuesForTable, valuesForChart
	let dailyTable, dailyChart
	const timeseries = props.timeseries
	valuesForTable = calcDailyMergeSplit(timeseries.daily)
	valuesForChart = calcDailyMergeSplitChart(timeseries.daily)
	dailyTable = (
		<Panel size={6} title='Stats per Day'>
			<Griddle results={valuesForTable} enableInfiniteScroll={true} useFixedHeader={true} bodyHeight={400} />
		</Panel>
	)
	dailyChart = (
		<Panel size={6} title='Daily Chart'>
			<ReactHighcharts config={valuesForChart} />
		</Panel>
	)
	return (
		<Section title={props.title} >
			{dailyTable} {dailyChart}
		</Section>
	)
}

export const UserSection = (props) => {
	let userMergeSplitTableValues, userChartValues, activityTraceData, bodyBoxPlotData
	let userTable, activityTrace, userChart, userBodyBoxPlot
	const user = props.user
	userMergeSplitTableValues = calcUserMergeSplitTable(user)
	userChartValues = calcUserChartValues(user)
	activityTraceData = calcActivityTraceData(user)
	bodyBoxPlotData = calcUserBodyTimeChart(user)
	userTable = (
		<Panel size={6} title='Total Statistics by User'>
			<Griddle results={userMergeSplitTableValues} enableInfiniteScroll={true} useFixedHeader={true} bodyHeight={400} />
		</Panel>
	)
	const classMap = {'working': 'DarkTurquoise', 'default': 'white'}
	const scrollWindowStyle = {
		position: 'relative',
		overflowY: 'scroll',
		height: '400px',
		width: '100%'
	}
	activityTrace = (
		<Panel size={6} title='Activity Trace for Proofreaders' >
			<div style={scrollWindowStyle}>
				<ActivityTrace barwidth={400}  data={activityTraceData} height={15} colors={classMap} byweek={false}  />
			</div>
		</Panel>
	)
	let innerCharts = []
	userChartValues.forEach((item) => {
		if (Object.keys(item).length > 0) {
			innerCharts.push(<ReactHighcharts config={item} />)
		}
	}) 
	userChart = (
		<Panel size={6} title='Daily Merges and Splits by Proofreader' >
			<div style={scrollWindowStyle}>
				{innerCharts}
			</div>
		</Panel>
	)
	userBodyBoxPlot = (
		<Panel size={6} title='User Body Split Time'>
			<ReactHighcharts config={bodyBoxPlotData} />
		</Panel>
	)

	
	return (
		<Section title={props.title} >
			<Row>
				{userTable} 
				{activityTrace}
			</Row>
			<Row>
				{userChart}
				{userBodyBoxPlot}
			</Row>
		</Section>
	)
}

export const Row = (props) => {
	let content
	if (props.children) {
		content = props.children
	}
	return (<div className='row'>{content}</div>)
}
