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
import CreateInstance from "components/Dialog/CreateInstance";
import UpdateImage from "components/Dialog/UpdateImage";
import axios from 'axios';

import dashboardStyle from "assets/jss/material-dashboard-react/views/dashboardStyle.jsx";
// import { createNoSubstitutionTemplateLiteral } from "typescript";


class Dashboard extends React.Component {

  handleChange = (event, value) => {
    this.setState({ value });
  };

  handleChangeIndex = index => {
    this.setState({ value: index });
  };

  createInstanceCallback = async (stackName, instanceName, flavor, image) =>{
    let stackInfo={
      "token": this.props.location.state.token,
      "server_name": instanceName,
      "stack_name": stackName,
      "flavor": flavor,
      "image": image,
      "project_id" : this.props.location.state.project_uuid,
    };
    fetch(this.API_BASE+'/createStack',{
      method: 'POST',
      headers:{
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(stackInfo)
      }).then((response)=> response.json())
      .then((responseData)=>{
        console.log(responseData)
    });
  }

  // updateImageCallback = async ( file, imageName, imageDescription) => {
  //   let stackInfo={
  //     token: this.props.location.state.token,
  //     file: file,
  //     imageName:  imageName,
  //     imageDescription: imageDescription
  //   };
  //   console.log(stackInfo)
  //   fetch(this.API_BASE+'/uploadImage',{
  //     method: 'POST',
  //     headers:{
  //       'Content-Type': 'application/json'
  //     },
  //     body: JSON.stringify(stackInfo)
  //     }).then((response)=> response.json())
  //     .then((responseData)=>{
  //       console.log(responseData)
  //       return({
  //         'result': 'True'
  //       })
  //     });
  // }


   async updateImageCallback(file, imageName, imageDescription){
    const toBase64 = file => new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = error => reject(error);
    });
   
    const data = {
      title: imageName,
      file: await toBase64(file),
      desc: imageDescription
    }
   
    // submitForm("application/json", data, (msg) => console.log(msg));
    console.log(data)
    axios({
      url: this.API_BASE+'/upload',
      method: 'POST',
      data: data,
      headers: {
      'Content-Type': "application/json"
      }
      }).then((response) => {
        console.log(response.data);
      }).catch((error) => {
        console.log(error)
        console.log("error");
      })
  }


  getInstanceInfo = async () => {
    
    const settings = {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      }
    }
    const response = await fetch(this.API_BASE+'/instanceInfo?'+ "token=" + this.props.location.state.token, settings);
    if (!response.ok) throw Error(response.message);
    try {
      const data = await response.json();
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
      this.getInstanceInfo();  
    } catch(e){
      console.log(e);
    }
  }

  constructor(props){
    super(props);
    this.state = {
      value: 0,
      instance_list:[
      ],
      project_id: null
    };
    this.API_BASE = 'http://localhost:5000'
    this.mounted = false;
    this.updating();
    this.interval = setInterval(() => {
      if(this.mounted) this.updating();
    },30000)  
  }

  render() {
    return (
      <div>
        <CreateInstance token = {this.props.location.state.token} callbackFromParent={this.createInstanceCallback}/>
        <UpdateImage submitForm = {this.submitForm} callbackFromParent={this.updateImageCallback}/>
        <InstanceList token = {this.props.location.state.token} instance_list = {this.state.instance_list}  classes = {this.props.classes} />
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
