
function validateForm() {
    try {
      let allVisitorsFieldWrapper = document.getElementById('visitors_list_container');
      let allVisitors = allVisitorsFieldWrapper.getElementsByTagName('input');
      let allCarsFieldWrapper = document.getElementById('cars_list_container');
      let allCars = allCarsFieldWrapper.getElementsByTagName('input');

      let from_date = new Date(document.querySelector('#from_date').value);
      const to_date =  new Date(document.querySelector('#to_date').value);

      if (from_date > to_date) {
        $('#dateValidationErrorModal').modal('show');
        return false;
      }

      if (allVisitors.length === 0 && allCars.length === 0) {
        $('#validationErrorModal').modal('show');
        return false;
      }
    } catch (e) {
        console.log(e);
        return false
    }


}