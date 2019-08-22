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
        id: 0,
        name: 'NONE',
        cpu: 1,
        memory: 2,
        disk: 3,
        rating: 4
      },
      {
        id: 1,
        name: 'NONE',
        cpu: 5,
        memory: 6,
        disk: 7,
        rating: 8
      }
    ]
  };
  handleChange = (event, value) => {
    this.setState({ value });
  };

  handleChangeIndex = index => {
    this.setState({ value: index });
  };

  startCheck = function(){
      setInterval(()=>{
        this.updating();
      }, 5000)
  }

  updating = () =>{
    
  }

  render() {
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
