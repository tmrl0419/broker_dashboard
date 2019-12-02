
import React from 'react'
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import MenuItem from '@material-ui/core/MenuItem';

import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
    hidden: {
        display: 'none'
    }
});
    
class CreateInstance extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            stackName: '',
            instanceName: '',
            setFlavor: '',
            setImage:'',
            flavorList: [],
            imageList: [],
            open: false
        }

        this.handleFormSubmit = this.handleFormSubmit.bind(this)
        this.handleValueChange = this.handleValueChange.bind(this)
        this.handleClickOpen = this.handleClickOpen.bind(this)
        this.handleClose = this.handleClose.bind(this);
        this.handleSelectChange = this.handleSelectChange.bind(this);
        this.getCreateInfo = this.getCreateInfo.bind(this);
    }
    
    getCreateInfo = async () => {
        const settings = {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          }
        const response = await fetch('http://localhost:5000/createInfo?'+ "token=" + this.props.token, settings);
        if (!response.ok) throw Error(response.message);
        try {
            const data = await response.json();

            var flavors = [];
            for( var key in data['flavors']){
                flavors.push({
                    "value": data['flavors'][key],
                    "label": key
                })
            }

            var images = [];
            for( var key in data['images']){
                images.push({
                    "value": data['images'][key],
                    "label": key
                })
            }

            this.setState({
                flavorList: flavors,
                imageList: images
            })

        } catch (err) {
          console.log(err)
        }
    }

    handleFormSubmit(e) {
        e.preventDefault()
        this.props.callbackFromParent(this.state.stackName, this.state.instanceName, this.state.setFlavor, this.state.setImage)
            .then((response) => {
                console.log(response);
            })
        this.setState({
            open: false
        })
    }

    
    handleValueChange(e) {
        let nextState = {};
        nextState[e.target.name] = e.target.value;
        this.setState(nextState);
    }
    
    
    handleClickOpen() {
        this.getCreateInfo();
        this.setState({
            open: true
        });
    }
    
    
    handleClose() {
        this.setState({
            stackName: '',
            instanceName: '',
            setFlavor: '',
            setImage:'',
            flavorList: [],
            imageList: [],
            open: false
        })
    }

    handleSelectChange = e => {
        console.log(e)
        let nextState = {};
        nextState[e.target.name] = e.target.value;
        this.setState(nextState);
      };
    
    
    render() {
        const { classes } = this.props;
        return (
            <div>
            <Button variant="contained" color="primary" onClick={this.handleClickOpen}>
                Create Instance
            </Button>
            <Dialog open={this.state.open} onClose={this.handleClose}>
                <DialogTitle>Create Instance</DialogTitle>
                    <DialogContent>
                        <TextField label="Stack Name" type="text" name="stackName" value={this.state.stackName} onChange={this.handleValueChange} /><br/>
                        <TextField label="Instance Name" type="text" name="instanceName" value={this.state.instanceName} onChange={this.handleValueChange} /><br/>
                        <TextField 
                            label="Flavor"
                            select 
                            name="setFlavor" 
                            value={this.state.setFlavor} 
                            onChange={this.handleSelectChange}
                            SelectProps={{
                                MenuProps: {
                                  className: classes.menu,
                                },
                            }}
                            helperText="Please select Flavor"
                            margin="normal"
                        >
                            {this.state.flavorList.map(option => (
                                <MenuItem key={option.value} value={option.value}>
                                {option.value}
                                </MenuItem>
                            ))}
                        </TextField>
                        <br/>
                        <TextField 
                            label="Image"
                            select 
                            name="setImage" 
                            value={this.state.setImage} 
                            onChange={this.handleSelectChange}
                            SelectProps={{
                                MenuProps: {
                                  className: classes.menu,
                                },
                            }}
                            helperText="Please select Image"
                            margin="normal"
                        >
                            {this.state.imageList.map(option => (
                                <MenuItem key={option.value} value={option.value}>
                                {option.value}
                                </MenuItem>
                            ))}
                        </TextField>
                        <br/>
                    </DialogContent>
                <DialogActions>
                <Button variant="contained" color="primary" onClick={this.handleFormSubmit}>OK</Button>
                <Button variant="outlined" color="primary" onClick={this.handleClose}>Close</Button>
                </DialogActions>
            </Dialog>
        </div>
        )
    }
    
}    
export default withStyles(styles)(CreateInstance);
