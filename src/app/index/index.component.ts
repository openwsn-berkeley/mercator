import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import {Router, ActivatedRoute} from "@angular/router";
import {GithubService} from "../github.service";

@Component({
  selector: 'app-index',
  templateUrl: './index.component.html',
  styleUrls: ['./index.component.css']
})
export class IndexComponent implements OnInit {

  path: string[] = Array();
  tree: string[][] = Array();

  @ViewChild('chartContainer') chartContainer: ElementRef;

  constructor(private gith:GithubService, private router: Router, private route: ActivatedRoute) {
    // get site names
    this.gith.getSites().subscribe((res: any) => {
      let localsites = [];
      res.forEach( function(item){ localsites.push(item.name); });
      this.tree[0] = localsites
    });
  }

  ngOnInit() {
  }

  getFiles(level,file) {
    // update path
    this.path[level] = file;

    // removing subpath
    this.path = this.path.slice(0,level+1);
    this.tree = this.tree.slice(0,level+1);

    // convert path array to single string
    let str_path = this.path.join('/');

    if (file.includes(".json")){
      this.router.navigate(this.path, { relativeTo: this.route });
    }
    else {
      this.gith.getFiles(str_path).subscribe((res: any) => {
        let localfiles = [];
        res.forEach( function(item){ localfiles.push(item.name); });
        this.tree[level+1] = localfiles
      });
    }
  }
}
