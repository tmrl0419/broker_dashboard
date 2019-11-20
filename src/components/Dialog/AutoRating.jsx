
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
    
    
class AutoRating extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            interval: null,
            open: false
        }
        this.handleFormSubmit = this.handleFormSubmit.bind(this)
        this.handleValueChange = this.handleValueChange.bind(this)
        // this.addCustomer = this.addCustomer.bind(this)
        this.handleClickOpen = this.handleClickOpen.bind(this)
        this.handleClose = this.handleClose.bind(this);
        this.update = this.update.bind(this);
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
          });
    }

    handleFormSubmit(e) {
        e.preventDefault()
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
        this.setState({
            open: true
        });
    }
    
    
    handleClose() {
        this.setState({
            file: null,
            userName: '',
            birthday: '',
            gender: '',
            job: '',
            fileName: '',
            open: false
        })
    }
    
    render() {
        const { classes } = this.props;
        return (
            <div>
            <Button variant="contained" color="primary" onClick={this.handleClickOpen}>
                Auto Rating
            </Button>
            <Dialog open={this.state.open} onClose={this.handleClose}>
                <DialogTitle>Auto Rating</DialogTitle>
                    <DialogContent>
                        <TextField label="Rating 조사 주기 (분)" type="text" name="interval" value={this.state.interval} onChange={this.handleValueChange} /><br/>
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
export default withStyles(styles)(AutoRating);
