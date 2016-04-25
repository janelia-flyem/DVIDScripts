
const initialState = {
  url: '',
  payload: {}
}
const getData = (state = initialState, action) => {
  switch (action.type) {
    case 'LOAD_FROM_DVID':
      return Object.assign({}, state, {
        url: action.url,
        payload: action.payload,
      })
    default:
      return state
  }
}

export default getData
