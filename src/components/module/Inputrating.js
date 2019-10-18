import React, { Component } from 'react';
import Instance from "../InstanceList/Instance";


class Inputrating extends Component {
  state = {
    namec : 0,
    showPopup : true
  }

  handleChange = (e) => {
    this.setState({
      namec: e.target.value
    })
    console.log(e.target.value)
    return <div> <Instance rating = {e.target.value}/> </div>
  }

  render() {
    return (
      <form>
        <input
          placeholder="rating"
          value={this.state.namec}
          onChange={this.handleChange.bind(this)}
          name = "name"
        />
      </form>
    );
  }
}

export default Inputrating;