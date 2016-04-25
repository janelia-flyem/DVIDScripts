import React from 'react'
import {connect} from 'react-redux'
import {loadStatsFromDVID} from './actions'
import 'whatwg-fetch'

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
		//console.log("Mounted");
	},
	componentDidMount: function() {
		const dvid_api_url = `${this.props.dvid_url}/api/node/${this.props.uuid}/external_dashboard/key/dashboard`
		fetch(dvid_api_url).then( (response) => {
			return  response.json()
		}).then( (r) => {
			this.props.fetchFromDVID(dvid_api_url, r)
		})
	},
	componentWillUnmount: function() {
		//console.log('Unmounting')
	},
	render: function() {
		let merges, splits;
		console.log(this.props.payload)
		if (this.props.payload) {
			merges = <SingleStat stat_name='Merges' stat_value={this.props.payload.overall.merges} />
		}
		if (this.props.payload) {
			splits = <SingleStat stat_name='Splits' stat_value={this.props.payload.overall.splits} />
		}
		return <div className='row' >{merges}{splits} </div>
	}
});

var mapStateToProps = function(state){
    return {
    	url: state.url,
    	payload: state.payload
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