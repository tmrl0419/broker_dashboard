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
    
    
class StackUpdate extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            rating: null,
            open: false
        }
        this.handleFormSubmit = this.handleFormSubmit.bind(this)
        this.handleValueChange = this.handleValueChange.bind(this)
        // this.addCustomer = this.addCustomer.bind(this)
        this.handleClickOpen = this.handleClickOpen.bind(this)
        this.handleClose = this.handleClose.bind(this);
    }
    
    handleFormSubmit(e) {
        e.preventDefault()
        this.props.callbackFromParent(this.state.rating);
        this.setState({
            rating: null,
            open: false
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
            rating: null,
            open: false
        })
    }


    render() {
        const { classes } = this.props;
        return (
            <div>
                <Button variant="contained" color="primary" onClick={this.handleClickOpen}>
                    Stack Update
                </Button>
                <Dialog open={this.state.open} onClose={this.handleClose}>
                    <DialogTitle>Rating 조사</DialogTitle>
                        <DialogContent>
                            <TextField label="Rating" type="text" name="rating" value={this.state.rating} onChange={this.handleValueChange} /><br/>
                        </DialogContent>
                    <DialogActions>
                    <Button variant="contained" color="primary" onClick={this.handleFormSubmit}>Update</Button>
                    <Button variant="outlined" color="primary" onClick={this.handleClose}>Close</Button>
                    </DialogActions>
                </Dialog>
            </div>
        )
    }
    
}    
export default withStyles(styles)(StackUpdate);
