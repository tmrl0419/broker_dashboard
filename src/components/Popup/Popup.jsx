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
import Button from "components/CustomButtons/Button"
import dashboardStyle from "assets/jss/material-dashboard-react/views/dashboardStyle.jsx";
import withStyles from "@material-ui/core/styles/withStyles";

class Popup extends React.Component {
  constructor(){
    super(...arguments);
    this.state ={
        uuid:'' 
    };
  }

  handleRadio( event ) {
    console.log(this.state.uuid)
    this.setState({uuid: event.target.name})
  }

  onSubmit( uuid ) {
		let userInfo={
			'id':this.props.UserID,
      'password':this.props.Password,
      'uuid': uuid
    };
    console.log(userInfo)
		fetch('http://localhost:5000/login/project',{
			method: 'POST',
			headers:{
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(userInfo)
	    }).then((response)=> response.json())
	    .then((responseData)=>{
	    	if(responseData.loginresult){
          // direct to dashboard
        }
	    	else{
          // redicrect to login
	    	}
      });
    }
    
  render() {
    const list = this.props.projects.map(
      (info) => (        
      <label>
        <input type="radio" name={info} value={info} onChange={this.handleRadio} />
        {info}
      </label>)); 
    
    return(
      <div>
        {list}
        <div>
          <Button color = "success" onClick={this.onSubmit.bind(this)}>LOG IN</Button>
        </div>
      </div>   
    );
  }
}
export default withStyles(dashboardStyle)(Popup);
