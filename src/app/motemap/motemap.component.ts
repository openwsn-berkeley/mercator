import { Component, ViewChild } from '@angular/core';
import {AfterViewInit} from "@angular/core";
import {GithubService} from "../github.service";
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-motemap',
  templateUrl: './motemap.component.html',
  styleUrls: ['./motemap.component.css']
})


export class MotemapComponent implements AfterViewInit {
  context:CanvasRenderingContext2D;

  circles = [];
  site = "";
  exp = "pdr_freq";
  exp_type = "one_to_one";
  src_mac = "";
  dst_mac_list = [];

  @ViewChild("myCanvas") myCanvas;

  COLOR_DEFAULT = "black";

  constructor(private gith:GithubService, private route: ActivatedRoute,){
    let newcircles = [];

    this.route.params.subscribe(params => {
      this.site=params['site'];
    });

    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/data/metas/"+this.site+".json";

    this.gith.download_url(url).subscribe((res: any) => {
      res.forEach((node) => {
        if (node.mac) {
          newcircles.push({x: node.x, y: node.y, msg: node.mac, color: this.COLOR_DEFAULT});
        }
      });
    });
    this.circles = newcircles;
  }

  ngAfterViewInit() { }

  boom(circle_id, msg) {
    if (this.src_mac == "") {
      // new src mac
      this.src_mac = msg;
      this.circles.forEach((item) => {
        item.color = this.COLOR_DEFAULT;
      });
      this.circles[circle_id].color = "red";
    } else if (this.src_mac == msg) {
      // cancel src mac
      this.circles.forEach((item) => {
        item.color = this.COLOR_DEFAULT;
      });
      this.dst_mac_list = [];
      this.src_mac = "";
    } else {
      let found = -1;
      for (let i=this.dst_mac_list.length-1; i>=0; i--) {
        if (this.dst_mac_list[i] === msg) {
          found = i;
          break;
        }
      }
      if (found != -1){
          // cancel dst_mac
          this.dst_mac_list.splice(found, 1);
          this.circles[circle_id].color = this.COLOR_DEFAULT;
      } else {
        // new dst_mac
        this.dst_mac_list.push(msg);
        this.circles[circle_id].color = "green";
      }
      this.dst_mac_list = this.dst_mac_list.slice(); // update reference
    }
  }
}
