import { Component, OnInit } from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {GithubService} from "../github.service";

@Component({
  selector: 'app-pdr',
  templateUrl: './pdr.component.html',
  styleUrls: ['./pdr.component.css']
})
export class PdrComponent {

  site= ""

  types=[]



  constructor(private route: ActivatedRoute,private gith:GithubService) {

    this.route.params.subscribe(params => {

      this.site=params['city'];

      this.gith.getTypes(params['city']).subscribe((res: any) => {
        this.types = res;
      });

      })


  }

  ngOnInit() {
  }

}
