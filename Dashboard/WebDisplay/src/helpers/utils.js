export const calcDailyMergeSplit = (values) => {
	let table = {}
	table.dates = Object.keys(values)
	table.merges = table.dates.map((item) =>{
		return values[item].merges
	})
	table.splits = table.dates.map((item) =>{
		return values[item].splits
	})
	return table
}
