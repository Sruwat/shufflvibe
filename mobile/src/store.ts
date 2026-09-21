import { create } from 'zustand';
import { Action } from './algorithms';
import { Factor } from './data';
import { AssessmentState, createAssessment } from './fullEngine';
type Screen='welcome'|'intro'|'login'|'profile'|'instructions'|'assessment'|'reveal'|'discover'|'search'|'plans'|'rooms'|'profileHome'|'control';
type State={screen:Screen; assessmentIndex:number; scores:Partial<Record<Factor,number>>; actions:Record<string,Action>; assessment:AssessmentState; locked:boolean; userName:string; set:(p:Partial<State>)=>void; reset:()=>void};
export const useApp= create<State>((set)=>({screen:'welcome',assessmentIndex:0,scores:{},actions:{},assessment:createAssessment(),locked:true,userName:'Aarav',set:(p)=>set(p),reset:()=>set({screen:'welcome',assessmentIndex:0,scores:{},actions:{},assessment:createAssessment(),locked:true})}));
