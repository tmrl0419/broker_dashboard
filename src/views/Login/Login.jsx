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
// @material-ui/core components
// core components
import GridItem from "components/Grid/GridItem.jsx";
import GridContainer from "components/Grid/GridContainer.jsx";
import Card from "components/Card/Card.jsx";
import CardHeader from "components/Card/CardHeader.jsx";
import CardBody from "components/Card/CardBody.jsx";
import InputWithLabel from "components/InputWithLabel/InputWithLabel"
import Button from "components/CustomButtons/Button"
import dashboardStyle from "assets/jss/material-dashboard-react/views/dashboardStyle.jsx";
import withStyles from "@material-ui/core/styles/withStyles";
import SnackbarContent from "components/Snackbar/SnackbarContent.jsx";
import Admin from "layouts/Admin"
import Popup from "components/Popup/Popup"


class LoginPage extends React.Component {
  constructor(){
		super(...arguments);
		this.state ={
			ID:'',
      PW:'',
      showPopup: false,
      isWrong: false,
      projects: null,
      uuid: null
    };
		this.requestIDChange = this.requestIDChange.bind(this);
		this.requestPWChange = this.requestPWChange.bind(this);
  }
  
  togglePopup(pjs, uuides) {
    this.setState({
      isWrong: false,
      showPopup: !this.state.showPopup,
      projects: pjs,
      uuid: uuides
    });
  }


  onSubmit(){
		let userInfo={
			'id':this.state.ID,
			'password':this.state.PW
    };
    console.log(userInfo)
		fetch('http://localhost:5000/login',{
			method: 'POST',
			headers:{
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(userInfo)
	    }).then((response)=> response.json())
	    .then((responseData)=>{
	    	if(responseData.loginresult){
          console.log(responseData.projects)
          this.togglePopup(responseData.projects,responseData.uuid);
	    	}
	    	else{
          this.setState({
            requestPW:'',
            isWrong:true
          });
	    	}
	    });
  }

  requestIDChange(event){
		this.setState({ID: event.target.value});
	}
	requestPWChange(event){
		this.setState({PW: event.target.value});
	}

  render() {      
    const { classes } = this.props;
    return (
      <GridContainer>
        <GridItem md={12}>
          <Card>
            <CardHeader color="info">
              <h4 className={classes.cardTitleWhite}>LOGIN</h4>
            </CardHeader>
            <CardBody>
              <InputWithLabel label= "UserID" name= "email" placeholder = "UserID" value={this.state.requestID} onChange={this.requestIDChange}/>
              <InputWithLabel label= "PassWord" name="password" placeholder = "PW" value={this.state.requestPW} onChange={this.requestPWChange}/>
              <Button color = "info" onClick={this.onSubmit.bind(this)} >SIGN IN</Button>
              {this.state.isWrong ? <SnackbarContent message="Please Check UserID/Password" color="danger"/> :null }
            </CardBody>
            { this.state.showPopup && !this.state.isWrong ? 
            <Popup UserID = {this.state.ID} Password= {this.state.PW}projects = {this.state.projects} uuid = {this.state.uuid} text="SEX" closePopup={this.togglePopup.bind(this)} /> 
            :null }
          </Card>
        </GridItem>
      </GridContainer>
    );
  }
}

LoginPage.propTypes = {
  classes: PropTypes.object.isRequired
};

export default withStyles(dashboardStyle)(LoginPage);
