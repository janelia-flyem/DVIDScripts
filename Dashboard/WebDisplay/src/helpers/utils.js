
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
            Ratio:  calcMergeToSplitRatio(userVals[user].merges, userVals[user].splits)
        }
    })
    return table
} 
export const calcDaySnapshotData = (userVals) => {
    let daySnapshotData = {}
    const users = Object.keys(userVals)
    for (let i = 0; i < users.length; i++) {
        let user = users[i]
        daySnapshotData[user] = userVals[user].interval
    }
    return daySnapshotData
}