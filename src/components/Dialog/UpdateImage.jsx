import React from 'react'
// import { post } from 'axios';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import Button from '@material-ui/core/Button';
import { withStyles } from '@material-ui/core/styles';
import DialogContentText from '@material-ui/core/DialogContentText';
import TextField from '@material-ui/core/TextField';


const styles = theme => ({
    hidden: {
        display: 'none'
    }
});

class CustomerAdd extends React.Component {


    constructor(props) {
        super(props);
        this.state = {
            file: null,
            fileName: '',
            imageName: '',
            imageDescription: '',
            open: false
        }
        this.handleFormSubmit = this.handleFormSubmit.bind(this)
        this.handleFileChange = this.handleFileChange.bind(this)
        this.handleClickOpen = this.handleClickOpen.bind(this)
        this.handleClose = this.handleClose.bind(this)
        this.handleValueChange = this.handleValueChange.bind(this)
    }


    handleFormSubmit(e) {
        e.preventDefault()
        this.props.callbackFromParent(this.state.file, this.state.imageName, this.state.imageDescription)
            .then((response) => {
                // console.log(response.data);
                // this.props.stateRefresh();
            })
        this.setState({
            file: null,
            fileName: '',
            imageName: '',
            imageDescription: '',
            open: false
        })
    }


    handleFileChange(e) {
        this.setState({
            file: e.target.files[0],
            fileName: e.target.value
        });
    }


    handleClickOpen() {
        this.setState({
           open: true
        });
    }


    handleClose() {

        this.setState({
            file: null,
            fileName: '',
            imageDescription: '',
            open: false
        })

    }

    handleValueChange(e) {
        let nextState = {};
        nextState[e.target.name] = e.target.value;
        this.setState(nextState);
    }
    

    render() {

        const { classes } = this.props;
        return (
            <div>
                <Button variant="contained" color="primary" onClick={this.handleClickOpen}>
                    Upload Image
                </Button>
                <Dialog open={this.state.open} onClose={this.handleClose}>
                    <DialogTitle>Upload Image</DialogTitle>
                    <DialogContent>
                        <input className={classes.hidden} accept="*" id="raised-button-file" type="file" file={this.state.file} value={this.state.fileName} onChange={this.handleFileChange} />
                        <label htmlFor="raised-button-file">
                        <Button variant="contained" color="primary" component="span" name="file">
                            {this.state.fileName === ''? "Find image" : this.state.fileName}
                        </Button>
                        </label><br/>
                        <DialogContentText>
                            Select image 
                        </DialogContentText>
                            <TextField label="imageName" type="text" name="imageName" value={this.state.rating} onChange={this.handleValueChange} /><br/>
                            <TextField label="imageDescription" type="text" name="imageDescription" value={this.state.rating} onChange={this.handleValueChange} /><br/>
                        </DialogContent>
                    <DialogActions>
                        <Button variant="contained" color="primary" onClick={this.handleFormSubmit}>추가</Button>
                        <Button variant="outlined" color="primary" onClick={this.handleClose}>닫기</Button>
                    </DialogActions>
                </Dialog>
            </div>
        )

    }

}


export default withStyles(styles)(CustomerAdd)