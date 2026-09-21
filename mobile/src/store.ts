import { create } from 'zustand';
import { Action } from './algorithms';
import { Factor } from './data';
import { AssessmentState, createAssessment } from './fullEngine';
export type FeatureMode='venue'|'activePlan'|'arrival'|'feedback'|'hostRoom'|'joinRequests'|'capsule'|'notifications'|'inbox'|'chat'|'visitor'|'editProfile'|'history'|'privacy'|'settings'|'report'|'support';
type Screen='welcome'|'intro'|'login'|'profile'|'instructions'|'assessment'|'reveal'|'discover'|'search'|'plans'|'rooms'|'profileHome'|'control'|'feature';
type State={screen:Screen; featureMode:FeatureMode; assessmentIndex:number; scores:Partial<Record<Factor,number>>; actions:Record<string,Action>; assessment:AssessmentState; locked:boolean; userName:string; set:(p:Partial<State>)=>void; reset:()=>void};
export const useApp= create<State>((set)=>({screen:'welcome',featureMode:'settings',assessmentIndex:0,scores:{},actions:{},assessment:createAssessment(),locked:true,userName:'Aarav',set:(p)=>set(p),reset:()=>set({screen:'welcome',featureMode:'settings',assessmentIndex:0,scores:{},actions:{},assessment:createAssessment(),locked:true})}));
