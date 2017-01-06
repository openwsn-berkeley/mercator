/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { MotemapComponent } from './motemap.component';

describe('MotemapComponent', () => {
  let component: MotemapComponent;
  let fixture: ComponentFixture<MotemapComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MotemapComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MotemapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
