import random
from source.gui.api import Api
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import psignifit as ps
import psignifit.psigniplot as psp

class online_psychometric_curve(Api):
    def __init__(self):
        super().__init__()

        # Names of task variables coming from the board
        self.x_var      = 'current_RH'      # stimulus value / RH
        self.choice_var = 'choice'          # "left" / "right" / None
        self.err_var    = 'early_err_flag'  # flag for early/invalid trials

        # Containers for online psychometric data
        self.x_vals    = []  # unique stimulus values
        self.left_cnts = []  # number of "left" choices at each stimulus
        self.n_trials  = []  # total valid trials at each stimulus

        self.subject_ID = None
        self.file_path = None
        
    # runs at the start of session
    def run_start(self):
        plt.ion()  # interactive mode so we can update without blocking

        self.fig, self.ax = plt.subplots()

        # Black background
        self.fig.patch.set_facecolor('black')
        self.ax.set_facecolor('black')

        # White text / spines / ticks
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')

        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')

        try:
            self.fig.canvas.manager.set_window_title('Online psychometric curve')
        except Exception:
            pass

        self.x_vals    = []
        self.left_cnts = []
        self.n_trials  = []
        self.acc = 0

        self.ax.set_xlabel(self.x_var)
        self.ax.set_ylabel('P(left choice)')
        self.ax.set_ylim(-0.05, 1.05)

        self.subject_ID = self.board.data_logger.subject_ID
        
        if self.board.data_logger.file_path is not None:
            self.file_path = self.board.data_logger.file_path.replace('.tsv', '_psychometric.pdf')

        self.title_str = (self.subject_ID if self.subject_ID is not None else '') + \
                            datetime.now().strftime(' %Y-%m-%d')

        self.ax.set_title(self.title_str)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        plt.show(block=False)

    def _update_internal_counts(self, x_val, left_choice):
        """
        Update the running counts for a single completed, valid trial.
        x_val       : stimulus value
        left_choice : boolean, True if trial was a "left" choice
        """
        if x_val in self.x_vals:
            idx = self.x_vals.index(x_val)
            self.n_trials[idx] += 1
            if left_choice:
                self.left_cnts[idx] += 1
        else:
            # new stimulus level
            self.x_vals.append(x_val)
            self.n_trials.append(1)
            self.left_cnts.append(1 if left_choice else 0)

            # keep x_vals sorted (and keep counts aligned)
            order = np.argsort(self.x_vals)
            self.x_vals    = list(np.array(self.x_vals)[order])
            self.n_trials  = list(np.array(self.n_trials)[order])
            self.left_cnts = list(np.array(self.left_cnts)[order])

    def plot_update(self):
        """
        Recompute proportion and error bars and update the figure.
        """
        if len(self.x_vals) == 0:
            return

        try:
            x = np.array(self.x_vals, dtype=float)
            n = np.array(self.n_trials, dtype=float)
            k_left = np.array(self.left_cnts, dtype=float)

            p_left = k_left / n  # proportion of left choices

            # binomial standard error
            se = np.sqrt(p_left * (1.0 - p_left) / n)

            self.ax.clear()

            # Keep black background each redraw
            self.ax.set_facecolor('black')
            self.fig.patch.set_facecolor('black')

            # White ticks / labels / spines again (clearing resets them)
            self.ax.tick_params(colors='white')
            for spine in self.ax.spines.values():
                spine.set_color('white')

            self.ax.xaxis.label.set_color('white')
            self.ax.yaxis.label.set_color('white')
            self.ax.title.set_color('white')

            # Connect dots: line + markers, white on black
            self.ax.errorbar(
                x, p_left, yerr=se,
                fmt='-o',          # line + circle markers
                color='C0',     # line + marker color
                ecolor='C0',    # error bar color
                capsize=0
            )

            self.ax.set_xlabel(self.x_var)
            self.ax.set_ylabel('P(left choice)')
            self.ax.set_ylim(-0.05, 1.05)
            self.ax.set_title(f'{self.title_str} (N = {int(n.sum())}, accuracy {self.acc})')

            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

        except Exception as e:
            print("Error in plot_update():", repr(e))

    # this is called repeatedly during the session
    def process_data_user(self, data):
        """
        data['vars'] is a list of named tuples with fields .name and .value.

        We wait until we see a set of variables that includes:
            - current_RH          (stimulus)
            - choice              ("left"/"right"/None)
            - early_err_flag == 0 (valid trial)
        Then we treat that as one completed trial and update the psychometric.
        """
        try:
            if len(data['vars']) == 0:
                return

            # make a simple dict: name -> value
            vars_dict = {v.name: v.value for v in data['vars']}

            # ensure we have all needed variables
            if (self.x_var not in vars_dict or
                    self.choice_var not in vars_dict or
                    self.err_var not in vars_dict):
                return

            x_val  = vars_dict[self.x_var]
            err    = vars_dict[self.err_var]
            choice = vars_dict[self.choice_var]
            self.acc = vars_dict['overall_ave_correct'] if 'overall_ave_correct' in vars_dict else None

            # skip invalid / early-error trials
            if bool(err):
                return

            # make sure choice is defined
            if choice is None:
                return

            # Expecting string "left" or "right"
            if choice not in ("left", "right"):
                return

            left_choice = (choice == "left")

            # Update internal counts and redraw psychometric
            self._update_internal_counts(x_val, left_choice)

        except Exception as e:
            print("Error in process_data_user():", repr(e))

    def run_stop(self):
        # Optionally save the final figure and close it at end of session
        try:
            if hasattr(self, 'fig'):
                if self.subject_ID is not None:
                    # fit psychometric function
                    if sum(self.n_trials) > 5:
                        # fitting
                        data = np.column_stack((self.x_vals, self.left_cnts, self.n_trials))
                        res = ps.psignifit(data, experiment_type='yes/no', sigmoid='gauss', debug=True)

                        # params
                        PSE = res.threshold(0.5, unscaled=True)[0]
                        JND = (res.threshold(0.75, unscaled=True)[0] - res.threshold(0.25, unscaled=True)[0]) / 2

                        print(f"PSE: {PSE: 1.3f}, JND: {JND: 1.3f}, lapses: {res.parameter_estimate['gamma']:1.3f}, {res.parameter_estimate['lambda']:1.3f}, eta: {res.parameter_estimate['eta']:1.3e}")

                        # dump results in a npz file
                        if self.subject_ID is not None:
                            np.savez(self.file_path.replace('.pdf', '.npz'),
                                    data=data,
                                    parameter_estimate=res.parameter_estimate,
                                    parameter_confidence_intervals=res.confidence_intervals,
                                    PSE=PSE,
                                    JND=JND)
                        
                        # clear figure
                        self.ax.clear()

                        # Keep black background each redraw
                        self.ax.set_facecolor('black')
                        self.fig.patch.set_facecolor('black')

                        # White ticks / labels / spines again (clearing resets them)
                        self.ax.tick_params(colors='white')
                        for spine in self.ax.spines.values():
                            spine.set_color('white')

                        self.ax.xaxis.label.set_color('white')
                        self.ax.yaxis.label.set_color('white')
                        self.ax.title.set_color('white')

                        # plot
                        psp.plot_psychometric_function(res, line_color='w', data_color='C0', ax=self.ax, estimate_type='mean')

                        self.ax.set_xlabel(self.x_var)
                        self.ax.set_ylabel('P(left choice)')
                        self.ax.set_ylim(-0.05, 1.05)
                        self.ax.set_title(f'{self.title_str} \n(N = {sum(self.n_trials):g}, accuracy {self.acc:1.2f}, JND {JND:1.1f}, PSE {PSE:1.1f})')

                        self.fig.canvas.draw()
                        self.fig.canvas.flush_events()

                    self.fig.savefig(self.file_path)
                
                # plt.close(self.fig)

        except Exception as e:
            print("Error in online_psychometric_curve.run_stop():", repr(e))

