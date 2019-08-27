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
import { thisExpression } from "@babel/types";

class Dashboard extends React.Component {
  state = {
    value: 0,
    instance_list:[
      {
        name: 'NONE',
        cpu: 1,
        memory: 2,
        disk: 3,
        rating: 4
      },
      {
        name: 'NONE',
        cpu: 5,
        memory: 6,
        disk: 7,
        rating: 8
      }
    ],
    token: "gAAAAABdZUKVDlqv63snne_Edr44fCWkSyF4cqJlRnJYIZxcOpZNILFnGwbDFuraRMczYS3L8nhHNlm1TIdssa-vbjzTNB1NYxmYV15MQsU_ctfBDjQDVZSLnRq_6brv-XVNwDlmPe8eMwZTY1KNK0O6jY1kb2--a0R_0tV8PhJkslg-EmAsaLg"
  };
  handleChange = (event, value) => {
    this.setState({ value });
  };

  handleChangeIndex = index => {
    this.setState({ value: index });
  };

  startCheck = function(){
      clearInterval(this.startCheck);
      setInterval(()=>{
        this.updating();
      }, 5000)
  }

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

    const response = await fetch('http://localhost:5000/instanceInfo?'+ "token=" + this.state.token, settings);
    if (!response.ok) throw Error(response.message);
    try {
      const data = await response.json();
      const temp = data['data']
      console.log(data)
      this.setState({
        instance_list: [temp]
      })
      return data;
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
    this.startCheck();
  }

  render() {
    console.log("rerender")
    const { classes } = this.props;
    return (
      <div>
        <InstanceList instance_list = {this.state.instance_list} />
        <Graph/>
        <Board/>
      </div>
    );
  }
}

Dashboard.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(dashboardStyle)(Dashboard);
