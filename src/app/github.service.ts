import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import 'rxjs/add/operator/map';

@Injectable()
export class GithubService {

  private b_url = "https://api.github.com/repos/openwsn-berkeley/mercator/contents/datasets/processed"

  constructor(private _http: Http) { }

  getSites(){
    var url = this.b_url+"?ref=develop"
    return this._http.get(url)
              .map((r: Response) => r.json());
  }
  getExps(site){
    var url = this.b_url+"/"+site+"?ref=develop";
    return this._http.get(url)
              .map((r: Response) => r.json());
  }
  getTypes(site){
    var url = this.b_url+"/"+site+"/pdr_freq?ref=develop";
    return this._http.get(url)
      .map((r: Response) => r.json());
  }
  getMacs(site,exp,type){
    var url = this.b_url+"/"+site+"/"+exp+"/"+type+"?ref=develop";
    return this._http.get(url)
              .map((r: Response) => r.json());
  }

  download_url(url){

  return this._http.get(url).map((r: Response) => r.json());
}



}