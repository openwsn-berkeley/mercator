import { Injectable } from '@angular/core';
import { Http, Response } from '@angular/http';
import 'rxjs/add/operator/map';
import {Observable} from "rxjs";

@Injectable()
export class GithubService {

  public b_url = "https://api.github.com/repos/openwsn-berkeley/mercator/contents/datasets/processed";

  constructor(private _http: Http) { }

  getSites(){
    var url = this.b_url+"?ref=data";
    return this._http.get(url)
              .map((r: Response) => r.json());
  }
  getExps(site, date){
    var url = this.b_url + "/" + site + "/" + date + "?ref=data";
    return this._http.get(url)
              .map((r: Response) => r.json());
  }
  getTypes(site, date, exp){
    var url = this.b_url + "/" + site + "/" + date + "/" + exp + "?ref=data";
    return this._http.get(url)
      .map((r: Response) => r.json());
  }
  getMacs(site,exp,type){
    var url = this.b_url+"/"+site+"/"+exp+"/"+type+"?ref=data";
    return this._http.get(url)
              .map((r: Response) => r.json());
  }

  getFiles(url){
    return this._http
      .get(this.b_url+"/"+url+"?ref=data")
      .map(this.extractData)
      .catch(this.handleError);
  }

  download_url(url){
    return this._http
      .get(url)
      .map(this.extractData)
      .catch(this.handleError);
  }

  private extractData(res: Response) {
    let body = res.json();
    return body || { };
  }

  private handleError(error: Response){
    let errMsg: string = "Could not get file";
    console.log(errMsg);
    return Observable.throw(errMsg)
  }
}
