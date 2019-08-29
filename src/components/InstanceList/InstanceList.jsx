import React from "react";
// nodejs library to set properties for components
// react plugin for creating charts
// @material-ui/core
import withStyles from "@material-ui/core/styles/withStyles";
// @material-ui/icons

// core components
import Instance from "./Instance.jsx";
import dashboardStyle from "assets/jss/material-dashboard-react/views/dashboardStyle.jsx";
import { array } from "prop-types";

function InstanceList(props){
  const { instance_list } = props;
  const list = instance_list.map(
    (info) => (console.log(info),<Instance data = {info}/>)
  );
  return(
    <div>
      {list}
    </div>   
  );
}

export default withStyles(dashboardStyle)(InstanceList);
