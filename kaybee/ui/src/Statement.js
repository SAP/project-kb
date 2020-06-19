import React, { Component } from 'react';
// import PropTypes from 'prop-types';
// import WizardFormFirstPage from './WizardFormFirstPage';
// import WizardFormSecondPage from './WizardFormSecondPage';
// import WizardFormThirdPage from './WizardFormThirdPage';
// import WizardFormFourthPage from './WizardFormFourthPage';

class Statement extends Component {
  constructor(props) {
    super(props);
    this.vuln_id = props.vuln_id
  }
  

  render() {
  
    return (
      <div>
        <div>Vulnerability identifier: {this.vuln_id}</div>
        <div>
            <b>Aliases</b>
        </div>
        <div>
            <b>Notes</b>
        </div>
        <div>
            <b>References</b>
        </div>
        <div>
            <b>Fixes</b>
        </div>
      </div>
    );
  }
}

export default Statement;
