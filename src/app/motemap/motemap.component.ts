import { Component, ViewChild } from '@angular/core';
import {AfterViewInit} from "@angular/core";
import {GithubService} from "../github.service";

@Component({
  selector: 'app-motemap',
  templateUrl: './motemap.component.html',
  styleUrls: ['./motemap.component.css']
})
export class MotemapComponent implements AfterViewInit {
  context:CanvasRenderingContext2D;

  circles = [];
  site = "strasbourg";
  exp = "pdr_freq";
  src_mac = "";
  dst_mac_list = [];

  @ViewChild("myCanvas") myCanvas;

  constructor(private gith:GithubService){
    let url = "https://raw.githubusercontent.com/openwsn-berkeley/mercator/develop/metas/locations.json";
    let newcircles = [];
    this.gith.download_url(url).subscribe((res: any) => {
      res.forEach( function(item){
        if (item.location == "strasbourg") {
          item.nodes.forEach( function(node){
            if (node.mac) {
              newcircles.push({x: node.x, y: node.y, msg: node.mac, color: "black"});
            }
          });
        }
      });
    });
    this.circles = newcircles;
  }

  ngAfterViewInit() { }

  boom(circle_id, msg){
    if (this.src_mac == "") {
      // new src mac
      this.src_mac = msg;
      this.circles.forEach(function (item) {
        item.color = "black";
      });
      this.circles[circle_id].color = "red";
    } else if (this.src_mac == msg){
      // cancel src mac
      this.circles.forEach(function (item) {
        item.color = "black";
      });
      this.dst_mac_list = [];
      this.src_mac = "";
    } else {
      // new dst_mac
      this.dst_mac_list.push(msg);
      this.dst_mac_list = this.dst_mac_list.slice();
      this.circles[circle_id].color = "green";
    }
  }
}
