import {createAction, handleActions} from 'redux-actions'
// import * as TYPE from '../../stringType'

// 액션 타입을 정의해줍니다.
const TOGGLESTATE = 'listInfoForm/TOGGLESTATE'
const OPENPOPUP = 'listInfoForm/OPENPOPUP'
const CLOSEPOPUP = 'listInfoForm/CLOSEPOPUP'
const NEXTSTATUS = 'listInfoForm/NEXTSTATUS'
const PREVSTATUS = 'listInfoForm/PREVSTATUS'
const HANDLEINPUT = 'listInfoForm/HANDLEINPUT'
const HANDLEMARKETINGTYPE = 'listInfoForm/HANDLEMARKETINGTYPE'
const HANDLEKEYWORD = 'listInfoForm/HANDLEKEYWORD'
const HANDLEMARKETINGDATE = 'listInfoForm/HANDLEMARKETINGDATE'
const ADDINFO = 'listInfoForm/ADDINFO'
const HANDLEINFOLISTINPUT = 'listInfoForm/HANDLEINFOLISTINPUT'
const UPDATESTATUS = 'listInfoForm/UPDATESTATUS'
const SETSTATE = 'listInfoForm/SETSTATE'

//액션을 생성해 줍니다
export const toggleState = createAction(TOGGLESTATE)
export const openPopup = createAction(OPENPOPUP)
export const closePopup = createAction(CLOSEPOPUP)
export const nextStatus = createAction(NEXTSTATUS)
export const prevStatus = createAction(PREVSTATUS)
export const handleInput = createAction(HANDLEINPUT)
export const handleMarketingType = createAction(HANDLEMARKETINGTYPE)
export const handleKeyword = createAction(HANDLEKEYWORD)
export const handleMarketingDate = createAction(HANDLEMARKETINGDATE)
export const addInfo = createAction(ADDINFO)
export const handleInfoListInput = createAction(HANDLEINFOLISTINPUT)
export const updateStatus = createAction(UPDATESTATUS)
export const setState = createAction(SETSTATE)

const initialState = {
    popupState : false
}

export default handleActions({
    [TOGGLESTATE] : (state, action) => {
        console.log("toggle")
        return{
            ...state,
            popupState : !state.popupState
        }
    },

    [CLOSEPOPUP] : (state) => {
        const bodytag = document.getElementsByTagName('body')[0]
        bodytag.style.overflow = 'auto'
        return initialState
    },

    [OPENPOPUP] : (state, action) => {
        const bodyTag = document.getElementsByTagName('body')[0]
        bodyTag.style.overflow = 'hidden'
        console.log("open")
        return {
            ...state,
            popupState : true
        }
    }
},initialState)
