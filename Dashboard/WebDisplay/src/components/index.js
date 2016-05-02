import React from 'react'
import Griddle from 'griddle-react'
import ReactHighcharts from 'react-highcharts' 
//import DaySnapshot from '../components/day_snapshot'
import ActivityTrace from 'react-activity-trace'


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
	if (props.type === 'table') {
		content = <Griddle results={props.value} enableInfiniteScroll={true} useFixedHeader={true} bodyHeight={400} />
	}
	else if (props.type === 'chart') {
		console.log(props.value)
		content = <ReactHighcharts config={props.value} />
	}
	else if (props.type === 'daysnapshot') {
		const classMap =  {working: 'DarkTurquoise', default: 'white'};
		console.log(props.value);
		<ActivityTrace barwidth={400}  data={props.value} height={15} colors={classMap} byweek={false}  />
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



// export const Table = (props) => {
// 	console.log(dt)
// 	const header_list = Object.keys(props.data)
// 	const data_length = props.data[header_list[0]].length
// 	console.log('Data_length', data_length)
// 	let header = header_list.map( (item) => {
// 		let key = 'th_' + item
// 		return <th key={key}>{item}</th>
// 	})
// 	let body = []
// 	for (let i = 0; i < data_length; i++){
// 		let key = `tr_${i}`
// 		body.push(

// 			<tr key={key}> 
// 			{ 
// 				header_list.map( (item) => {
// 					let key = `td_${i}_${item}`
// 					return <td key={key}>{props.data[item][i]}</td>
// 				})
// 			}
// 			</tr>

// 		)
// 	}
// 	return (
// 		<table className="table table-hover ">
// 			<thead>
// 				<tr>
// 					{header}
// 				</tr>
// 			</thead>
// 			<tbody>
// 				{body}
// 			</tbody>

// 		</table>
// 	)
// }
