
import React from 'react'
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';

const styles = theme => ({
    hidden: {
        display: 'none'
    }
});
    
class Threshold extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            cpu: null,
            memory: null,
            disk: null,
            open: false
        }
        this.handleFormSubmit = this.handleFormSubmit.bind(this)
        this.handleValueChange = this.handleValueChange.bind(this)
        this.handleClickOpen = this.handleClickOpen.bind(this)
        this.handleClose = this.handleClose.bind(this);
    }
    
    
    handleFormSubmit(e) {
        e.preventDefault()
        console.log(this.state)
        this.props.callbackFromParent(this.state)
        this.setState({
            open: false,
            cpu: null,
            memory: null,
            disk: null
        })
    }

    
    handleValueChange(e) {
        let nextState = {};
        nextState[e.target.name] = e.target.value;
        this.setState(nextState);
    }
    

    handleClickOpen() {
        this.setState({
            open: true
        });
    }
    
    
    handleClose() {
        this.setState({
            open: false,
            cpu: null,
            memory: null,
            disk: null
        })
    }
    
    
    render() {
        const { classes } = this.props;
        return (
            <div>
            <Button variant="contained" color="primary" onClick={this.handleClickOpen}>
                Aodh threshold
            </Button>
            <Dialog open={this.state.open} onClose={this.handleClose}>
                <DialogTitle>Aodh threshold</DialogTitle>
                    <DialogContent>
                        <TextField label="CPU Threshold (%)" type="text" name="cpu" value={this.state.birthday} onChange={this.handleValueChange} /><br/>
                        <TextField label="Memory Threshold (%)" type="text" name="memory" value={this.state.gender} onChange={this.handleValueChange} /><br/>
                        <TextField label="Disk Threshold (%)" type="text" name="disk" value={this.state.job} onChange={this.handleValueChange} /><br/>
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
export default withStyles(styles)(Threshold);
