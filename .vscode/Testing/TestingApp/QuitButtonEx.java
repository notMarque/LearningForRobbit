// Tutorial: https://zetcode.com/javaswing/firstprograms/

// Necessary Imports
import javax.swing.GroupLayout;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import java.awt.EventQueue;
import java.awt.Label;
import java.awt.Color;
import java.awt.Dimension;
import javax.swing.JFrame;
import javax.swing.JComponent;
import java.awt.event.KeyEvent;
import java.awt.event.MouseEvent;
import java.awt.event.MouseMotionAdapter;
import java.util.ArrayList;


class MyLabel extends JLabel {
    public MyLabel(String str) {
        super(str, CENTER);
    }

    @Override
    public boolean isOpaque() {
        return true;
    }
}

//JFrame serves as a top-level container that holds the components of the application
public class QuitButtonEx extends JFrame {

    // It's so called best practice not to put code in the constructor or something so it's been relegated to a function
    public QuitButtonEx() {
        initUI();
    }

    // Function Called by constructor
    private void initUI() {
        var parts = new ArrayList<JComponent>();   // Create an array of JComponents to pass to createLayout()

        var quitButton = new JButton("Quit");               //Create a button with the label "Quit"
        quitButton.addActionListener(e -> {this.dispose();});   //Plug an action listener into the button that disposes of the window
        quitButton.setToolTipText("Closes window");         // Create Tooltip text for button
        quitButton.setMinimumSize(new Dimension(120, 40));
        quitButton.setMnemonic(KeyEvent.VK_B);  // Calls quitButton on key event of alt b

        parts.add(quitButton); // Add quitButton to parts list

        var lbl = new MyLabel("Label Component For Text");                //create a colored label
        lbl.setMinimumSize(new Dimension(120, 40));    // Set the size
        lbl.setBackground(Color.BLUE);
        lbl.setForeground(Color.RED);
        parts.add(lbl);    // Add label to arraylist
        
        var coords = new JLabel("");
        coords.setMinimumSize(new Dimension(120, 40));
        parts.add(coords);
        
        var lbl2 = new JLabel("Label 2");
        lbl2.setMinimumSize(new Dimension(120, 40));
        parts.add(lbl2);

        createLayout(parts.toArray(new JComponent[0]));   //Create a layout from parts list transformed into an array
        
        addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseMoved(MouseEvent e) {
                super.mouseMoved(e);

                int x = e.getX();
                int y = e.getY();

                var text = String.format("X: %d  Y: %d", x, y);

                coords.setText(text);
            }
        });

        var webIcon = new ImageIcon(".vscode/resources/Robit.png");     // Creating an image to be used as the icon
        setIconImage(webIcon.getImage());    // Setting image as window icon
        
        
        setTitle("Quit Button");        //Set the title of the window
        setSize(400, 300);          //Set the size of the window
        setLocationRelativeTo(null);           //Sets the location of the window. In this case, the center of the screen
        setDefaultCloseOperation(EXIT_ON_CLOSE); //Sets the window to stop running when closed
    }

    private void createLayout(JComponent[] arg) {

        var pane = getContentPane();        // Creating a content pane where components are placed
        var gl = new GroupLayout(pane);     // Components are organized by the GroupLayout manager
        pane.setLayout(gl);

        gl.setAutoCreateContainerGaps(true);            //Creates gaps betweeen the components and the edge of the windows
        gl.setAutoCreateGaps(true);

        gl.setHorizontalGroup(gl.createParallelGroup()       //Creates a hohrizontal group and makes it the first with borders
                .addGroup(gl.createSequentialGroup()
                    .addComponent(arg[0])
                    .addComponent(arg[1]))
                .addGroup(gl.createSequentialGroup() // Adds a group to house the label
                    .addComponent(arg[2])
                    .addComponent(arg[3])));
                    
        gl.setVerticalGroup(gl.createSequentialGroup()          //Creates a vertical group and makes it the first with borders
                .addGroup(gl.createParallelGroup()
                    .addComponent(arg[0])
                    .addComponent(arg[1]))
                .addGroup(gl.createParallelGroup() // Adds a group to house the label
                    .addComponent(arg[2])
                    .addComponent(arg[3])));

        pack(); // Automatically sizes window based on size of components
    }

    public static void main(String[] args) {
        
        //Place the following commands on the event queue. Used to insure concurrency-safeness?
        EventQueue.invokeLater(() -> {
            var ex = new QuitButtonEx();   //Create a new instance of our function
            ex.setVisible(true);          //Make the window visible on screen
        });
    }
}