import React from 'react'

const SingleStat = React.createClass({
	render: function() {
		return <div className="col-lg-3">
				<div className="alert alert-info text-center">
					<h4>{this.props.stat_name}: <b>{this.props.stat_value} </b></h4>
				</div>
			</div>
	}

});

const App = React.createClass({
	getInitialState: function() {
		return {
			'merges': 12515,
			'splits': 5649,
		};
	},
	componentWillMount: function() {
		console.log("Mounted");
	},
	render: function() {
		let merges, splits;
		if (this.state.merges) {
			merges = <SingleStat stat_name='Merges' stat_value={this.state.merges} />
		}
		if (this.state.splits) {
			splits = <SingleStat stat_name='Splits' stat_value={this.state.splits} />
		}
		return <div className='row' >{merges}{splits} </div>
	}
});

export default App