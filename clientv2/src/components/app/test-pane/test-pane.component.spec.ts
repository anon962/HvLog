import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TestPaneComponent } from './test-pane.component';

describe('TestPaneComponent', () => {
  let component: TestPaneComponent;
  let fixture: ComponentFixture<TestPaneComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TestPaneComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(TestPaneComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
