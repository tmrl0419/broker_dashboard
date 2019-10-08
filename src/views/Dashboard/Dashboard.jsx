/*!

=========================================================
* Material Dashboard React - v1.7.0
=========================================================

* Product Page: https://www.creative-tim.com/product/material-dashboard-react
* Copyright 2019 Creative Tim (https://www.creative-tim.com)
* Licensed under MIT (https://github.com/creativetimofficial/material-dashboard-react/blob/master/LICENSE.md)

* Coded by Creative Tim

=========================================================

* The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

*/
import React from "react";
// nodejs library to set properties for components
import PropTypes from "prop-types";
// react plugin for creating charts
// @material-ui/core
import withStyles from "@material-ui/core/styles/withStyles";
// @material-ui/icons
// core components
import InstanceList from "components/InstanceList/InstanceList.jsx";
import Graph from "components/Graph/Graph.jsx";
import Board from "components/Board/Board.jsx";

import dashboardStyle from "assets/jss/material-dashboard-react/views/dashboardStyle.jsx";

class Dashboard extends React.Component {
  state = {
    value: 0,
    instance_list:[
      {
        name: "NULL",
        cpu: "0",
        memory: "0",
        disk: "0"
      }
      
    ],
    token: null
  };
  handleChange = (event, value) => {
    this.setState({ value });
  };

  handleChangeIndex = index => {
    this.setState({ value: index });
  };


  func = async () => {
    
    const settings = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'token': this.state.token
      },
      token: this.state.token
    }
    const response = await fetch('http://localhost:5000/instanceInfo?'+ "token=" + this.props.location.state.token, settings);
    if (!response.ok) throw Error(response.message);
    try {
      
      const data = await response.json();
      console.log(data);
      const temp = data['data'];
      if (temp!== 'undifined' && temp.length > 0){
        this.setState({
          instance_list: temp
        })
      }
    } catch (err) {
      console.log(err)
    }
  };

  async updating(){
    try{
      this.func();  
    } catch(e){
      console.log(e);
    }
  }

  constructor(props)
  {
    super(props);
    this.mounted = false;
    this.updating();
    this.interval = setInterval(() => {
      if(this.mounted) this.updating();
    },5000)  
  }

  render() {
    return (
      <div>
        <InstanceList instance_list = {this.state.instance_list} classes = {this.props.classes} />
        <Graph/>
        <Board/>
      </div>
    );
  }
  componentWillMount() {
    this.mounted = true;
  }

  componentWillUnmount(){
    this.mounted = false;
    clearInterval(this.state.startCheck)
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(dashboardStyle)(Dashboard);
