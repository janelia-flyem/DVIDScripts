
import ss from 'summary-statistics'

export const calcDailyMergeSplit = (values) => {
	const dates = Object.keys(values)
	let table = dates.map((item) =>{
		return {Date: formatDate(item),
			Merges: values[item].merges,
			Splits: values[item].splits
		}
	})
	return table.reverse()
}
export const formatDate = (datestr) => {
	const year = datestr.substr(0, 4)
	const month = datestr.substr(4, 2)
	const day = datestr.substr(6, 2)
	return `${year}-${month}-${day}`
}

export const calcDailyMergeSplitChart = (values) => {
	const dates = Object.keys(values)
	const merges = dates.map( (item) => {
		return values[item].merges
	})
	const splits = dates.map( (item) => {
		return values[item].splits
	})
	const prettyDates = dates.map( (item) => {
		return formatDate(item)
	})
	return {
		chart: {
			type: 'column'
		},
		title: {
			text: 'Daily Merges and Splits',
		},
		xAxis: {
			categories: prettyDates
		},
		yAxis: {
			title: {
				text: 'Count'
			},
			plotLines: [{
				value: 0,
				width: 1,
				color: '#808080'
			}]
		},
		legend: {
			layout: 'vertical',
			align: 'right',
			verticalAlign: 'middle',
			borderWidth: 0
		},
		series: [{
			name: 'Merges',
			data: merges
		}, {
			name: 'Splits',
			data: splits
		}]
	}
}

export const calcUserBodyTimeChart = (userVals) => {
	const users = Object.keys(userVals)
	// gets dates
	let series = [{
		name: 'Observations',
		data: []
	}]
	users.forEach((user) => {
		const dates = Object.keys(userVals[user].daily)
		let userData = []
		dates.forEach( (date) => {
			let bodyIDs = Object.keys(userVals[user].daily[date].bodies)
			bodyIDs.forEach((bodyID) => {
				let minutes = userVals[user].daily[date].bodies[bodyID].working / 60
				minutes = minutes.toFixed(1)
				userData.push(minutes)
			})
			
		})
		let quartiles = [0,0,0,0,0]
		if (userData.length > 0) {
			let stats = ss(userData)
			quartiles = [stats.min, stats.q1, stats.median, stats.q3, stats.max]
		}
		series[0].data.push(quartiles)
	})
	console.log(series)
	return ({
		chart: {
			type: 'boxplot'
		},
		title: {
			text: 'Body Split Time by User'
		},
		legend: {
			enabled: false
		},
		xAxis: {
			categories: users,
			title: {
				text: 'Users'
			}
		},
		yAxis: {
			title: {
				text: 'Body Split Time (minutes)'
			},
		},
		series: series
	})
}

const calcMergeToSplitRatio = (merges, splits) => {
	const ratio = (splits > 0)? (merges/splits).toFixed(2) : 0;
	return ratio
}

export const calcUserMergeSplitTable = (userVals) => {
	const users = Object.keys(userVals)
	const table = users.map((user) =>{
		return {Proofreader: user,
			Merges: userVals[user].merges,
			Splits: userVals[user].splits,
			Ratio:  calcMergeToSplitRatio(userVals[user].merges, userVals[user].splits),
			Bodies: Object.keys(userVals[user].bodies).length,
			Days: userVals[user].interval.length
		}
	})
	return table
} 
export const calcActivityTraceData = (userVals) => {
	let daySnapshotData = {}
	const users = Object.keys(userVals)
	for (let i = 0; i < users.length; i++) {
		let user = users[i]
		daySnapshotData[user] = userVals[user].interval
	}
	return daySnapshotData
}

export const  calcUserChartValues = (userVals) => {
	let chartjsons = []
	const users = Object.keys(userVals)
	for (let i = 0; i < users.length; i++) {
		const user = users[i]
		const dates = Object.keys(userVals[users[i]].daily)
		const merges = dates.map( (item) => {
			return userVals[user].daily[item].merges
		})
		const splits = dates.map( (item) => {
			return userVals[user].daily[item].splits
		})
		const bodies = dates.map( (item) => {
			let bodies_for_user = userVals[user].daily[item].bodies
			return Object.keys(bodies_for_user).length
		})
		const prettyDates = dates.map( (item) => {
			return formatDate(item)
		})
		chartjsons.push( {
			chart: {
				type: 'column'
			},
			title: {
				text: `Daily Merges and Splits for ${user}`,
			},
			xAxis: {
				categories: prettyDates
			},
			yAxis: {
				title: {
					text: 'Count'
				},
				plotLines: [{
					value: 0,
					width: 1,
					color: '#808080'
				}]
			},
			legend: {
				layout: 'vertical',
				align: 'right',
				verticalAlign: 'middle',
				borderWidth: 0
			},
			series: [{
				name: 'Merges',
				data: merges
			}, {
				name: 'Splits',
				data: splits
			}, {
				name: 'Bodies',
				data: bodies
			}]
		})
	}
	return chartjsons

}