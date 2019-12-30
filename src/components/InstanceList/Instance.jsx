import React from "react";
import Popup from "reactjs-popup";
// nodejs library to set properties for components
// react plugin for creating charts
// @material-ui/core
import Icon from "@material-ui/core/Icon";
// @material-ui/icons
import Store from "@material-ui/icons/Store";
import Warning from "@material-ui/icons/Warning";
import DateRange from "@material-ui/icons/DateRange";
import LocalOffer from "@material-ui/icons/LocalOffer";
import Update from "@material-ui/icons/Update";
import Accessibility from "@material-ui/icons/Accessibility";
// core components
import GridItem from "components/Grid/GridItem";
import GridContainer from "components/Grid/GridContainer";
import Danger from "components/Typography/Danger";
import Card from "components/Card/Card";
import CardHeader from "components/Card/CardHeader";
import CardIcon from "components/Card/CardIcon";
import CardFooter from "components/Card/CardFooter";
import AutoRating from "components/Dialog/AutoRating";
import StackUpdate from "components/Dialog/StackUpdate";
import Threshold from "components/Dialog/Threshold";
// import { LoopCircleLoading } from 'react-loadingg';
import ReactLoading from 'react-loading';

export default class Instance extends React.Component{

    constructor(props){
      super(props);
      this.state = {
        rating : 'not evaluated yet',
        cpu : null,
        memory : null,
        disk : null,
        name : null,
        Auto: false,
        Interval: null,
        processing: false
      };
      this.autoMode = this.autoMode.bind(this);
      this.update = this.update.bind(this);
      this.setTimer = this.setTimer.bind(this);
      // this.autoRatingCallback = this.autoRatingCallback.bind(this);
      // this.stackUpdateCallback = this.stackUpdateCallback.bind(this);
      var timer;
    }

    update = async () => {
      const { data,token }  = this.props
      let stackInfo={
        token: token,
        server_name: data.name,
        rating: this.state.rating,
        project_id : data.project_id
      };
      fetch('http://localhost:5000/stackUpdate',{
        method: 'POST',
        headers:{
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(stackInfo)
        }).then((response)=> response.json())
        .then((responseData)=>{
          console.log(responseData)
          if(responseData.result =='alternative'){
            console.log("Arrived");
            this.setState({
              processing:true
            });
          }
        });
    }

    setTimer = async ( threshold ) => {
      console.log(threshold)
      const { data,token }  = this.props
      let stackInfo={
        token: token,
        server_name: data.name,
        rating: this.state.rating,
        project_id : data.project_id,
        cpu: threshold.cpu,
        memory: threshold.memory,
        disk: threshold.disk
      };
      fetch('http://localhost:5000/setAlarm',{
        method: 'POST',
        headers:{
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(stackInfo)
        }).then((response)=> response.json())
        .then((responseData)=>{
          console.log(responseData);
        });
    }

    autoMode = (time) => { 
      var self = this;
      this.timer = setInterval( function(){
        self.update();
      }, time*1000 );
    }


    stackUpdateCallback = (childRating) =>{
      if(this.state.Auto == true) clearInterval(this.timer);
      this.setState({
        rating: childRating,
        Auto: false 
      }, () =>{
        this.update();
      });
    }

    autoRatingCallback = (childInterval) => {
      if ( typeof(childInterval) != 'number' || childInterval < 1){
        return;  
      }
      this.setState({
        Auto: true,
        Interval: childInterval
      }, () =>{
        this.autoMode(this.state.Interval)
      });
    }

    thresholdCallback = (data) =>{
      console.log(data);
      this.setTimer(data);
      this.setState({
        cpu: data.cpu,
        memory: data.memory,
        disk: data.disk
      })
    }

    render(){

      const classes = this.props.classes;
      const data  = this.props.data;

      return(
        <GridContainer>
          <Card xs={12} style={{flexDirection: 'row', justifyContent: 'flex-end' }}>
            <CardHeader color="primary" stats icon>
              <p className={classes.cardTitle} >{data.name}</p>
              { this.state.Auto ? <label className={classes.cardTitle} style={{color:'red'}} >Auto mode</label> : <label className={classes.cardTitle} style={{color:'blue'}}>Non- Auto mode</label>}
              {/* Add feature that clear loading bar, after finishing update or alternate*/}
              {this.state.processing || data.cpu==null || data.memory==null || data.disk==null? <ReactLoading type="spinningBubbles" color="black" height={200} width={100}/>:null}
            </CardHeader>
            <GridItem xs={12} sm={6} md={3}>
              <Card >  
                <CardHeader color="warning" stats icon>
                  <CardIcon color="warning">
                    <Icon>content_copy</Icon>
                  </CardIcon>
                  <p className={classes.cardCategory}>CPU</p>
                  <h3 className={classes.cardTitle}>
                    {data.cpu}<small>%</small>
                  </h3>
                  <p className={classes.cardCategory}>전체 : {data.flavor_cpu}개</p>
                  {this.state.cpu? <p style={{color:'red'}} className={classes.cardCategory}>Threshold : {this.state.cpu}%</p>: null}
                </CardHeader>
                <CardFooter stats>
                  <div className={classes.stats}>
                    <Danger>
                      <Warning />
                    </Danger>
                    <a href="#pablo" onClick={e => e.preventDefault()}>
                      Get more space
                    </a>
                  </div>
                </CardFooter>
              </Card>
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <Card>
                <CardHeader color="success" stats icon>
                  <CardIcon color="success">
                    <Store />
                  </CardIcon>
                  <p className={classes.cardCategory}>Memory</p>
                  <h3 className={classes.cardTitle}>{data.memory}<small>%</small></h3>
                  <p className={classes.cardCategory}>전체 : {data.flavor_memory}GB</p>
                  {this.state.memory? <p style={{color:'red'}} className={classes.cardCategory}>Threshold : {this.state.memory}%</p>: null}
                </CardHeader>
                <CardFooter stats>
                  <div className={classes.stats}>
                    <DateRange />
                    Last 24 Hours
                  </div>
                </CardFooter>
              </Card>
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <Card>
                <CardHeader color="danger" stats icon>
                  <CardIcon color="danger">
                    <Icon>info_outline</Icon>
                  </CardIcon>
                  <p className={classes.cardCategory}>Storage</p>
                  <h3 className={classes.cardTitle}>{data.disk}<small>%</small></h3>
                  <p className={classes.cardCategory}>전체 : {data.flavor_storage}GB</p>
                  {this.state.disk ? <p style={{color:'red'}}  className={classes.cardCategory}>Threshold : {this.state.disk}%</p> : null}
                </CardHeader>
                <CardFooter stats>
                  <div className={classes.stats}>
                    <LocalOffer />
                    Tracked from Github
                  </div>
                </CardFooter>
              </Card>
            </GridItem>
            <GridItem xs={12} sm={6} md={3}>
              <Card>
                <CardHeader color="info" stats icon>
                  <CardIcon color="info">
                    <Accessibility />
                  </CardIcon>
                  <p className={classes.cardCategory}>Rating</p>
                  <h3 className={classes.cardTitle}>{this.state.rating}<small>%</small></h3>
                </CardHeader>
                <CardFooter stats>
                  <div className={classes.stats}>
                    <Update />
                    Just Updated
                  </div>
                </CardFooter>
              </Card>
            </GridItem>
            <div>
              <StackUpdate data={data} token={this.props.token} callbackFromParent={this.stackUpdateCallback} />
              <AutoRating callbackFromParent={this.autoRatingCallback}/>
              <Threshold callbackFromParent={this.thresholdCallback}/>
            </div>
            
          </Card>
        </GridContainer>
      );
    }
}
